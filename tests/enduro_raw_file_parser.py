# coding=utf-8
import sys
import os
import logging

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(levelname)s: %(filename)s:%(lineno)d %(message)s')
logger = logging.getLogger(__file__)

from typing import Union
from datetime import datetime, timedelta, timezone
from collections import namedtuple, defaultdict
from enum import Enum
from threading import RLock

Disqualified = "DSQ"
DoNotStart = "DNS"
DidNotFinish = "DNF"
NotAvailable = "-"

HibpRawRecord = namedtuple("HibpRawRecord",
                           ("header", "playerno", "timestamp", "ms"))


class HibpPlayerMeta(object):
    def __init__(self, playerno, name, team, group):
        self.playerno = playerno
        self.name = name
        self.team = team
        self.group = group

    @classmethod
    def load_player_meta(cls, filename="riders_info.csv"):
        ret = defaultdict(list)
        try:
            with open(RawFile(filename).fullpath) as f:
                for line in f:
                    items = line.strip().split(',')
                    logger.debug(items)
                    h = cls(*items[:4])
                    ret[int(h.group)].append(h)
        except Exception as e:
            logger.error(e)
        finally:
            return ret


class HibpSingleTimeRecord():
    def __init__(self, start: datetime, end: datetime, result: timedelta):
        self.start = start
        self.end = end
        self.result = result

    def __str__(self):
        return f"{time_formatter(self.start)},{time_formatter(self.end)},{time_formatter(self.result)}"

    def __lt__(self, other):
        # start   |other dt | other str
        # self dt   |  cmp  |  >
        # self str  |  <    |  <
        # end      |        |
        # self dt  |   cmp  |  >
        # self str |   <    |  <
        if not isinstance(self.start, datetime):
            return True
        if not isinstance(other.start, datetime):
            return False
        if not isinstance(self.end, datetime):
            return True
        if not isinstance(other.end, datetime):
            return False
        return self.result > other.result

    def __eq__(self, other):
        if self.start == other.start == DoNotStart:
            return True
        if self.end == other.end == DidNotFinish:
            return True
        return self.result == other.result


DNSRecord = HibpSingleTimeRecord(DoNotStart, DoNotStart, DoNotStart)
IGRecord = HibpSingleTimeRecord(NotAvailable, NotAvailable, NotAvailable)


def time_formatter(t: Union[timedelta, datetime, str]) -> str:
    if isinstance(t, str):
        return t
    if isinstance(t, timedelta):
        t = datetime.fromtimestamp(0, tz=timezone.utc) + t
    return t.strftime("%H:%M:%S.%f")[:-3]


class HibpEnduroTimeRecord():
    def __init__(self, trans, stage, qualified=True, *, stage_config=None):
        self.trans = trans
        self.stage = stage
        self.qualified = qualified
        self.stage_config = stage_config

    def __lt__(self, other):
        # means slower here, or more time, or less points
        # both stage and trans result are same should be rare.
        if not self.qualified:
            return True
        if self.stage == other.stage:
            return self.trans > other.trans
        return self.stage > other.stage

    def __str__(self):
        if self.stage_config.has_trans:
            return f"{self.trans},{self.stage}"
        return str(self.stage)

    @property
    def scored(self):
        return self.qualified and isinstance(self.stage.result, timedelta)


HibpStageFullResult = namedtuple("HibpStageFullResult",
                                 ("player", "timeresult", "score"))


class HibpPlayerRecords():
    def __init__(self, player):
        self.player = player
        self.stage_results = []
        self.stage_scores = []
        self.finalscore = 0

    def __lt__(self, other):
        # means slower here, or more time, or less points
        if self.finalscore == other.finalscore:
            for i in range(len(self.stage_results) - 1, -1, -1):
                if self.stage_scores[i] == other.stage_scores[i]:
                    continue
                return self.stage_scores[i] < other.stage_scores[i]
        return self.finalscore < other.finalscore

    def __str__(self):
        s = f"{self.player.playerno},{self.player.name},{self.player.team},"
        for t, sr in zip(self.stage_results, self.stage_scores):
            s += f"{t},{sr},"
        return s + f"{self.finalscore}"


class RawFile():
    DIRPATH = os.path.dirname(__file__)

    def __init__(self, filename):
        self.filename = filename

    @property
    def fullpath(self):
        path = os.path.join(self.DIRPATH, self.filename)
        logger.debug(path)
        return path


class RacingMode(Enum):
    Enduro = 0
    Round = 1
    SingleShot = 2


class StageCommon():
    # this class decribes a stage's common meta info
    # for grouping specific meta, such as qualify_time for different group,
    # a Grouping stage object should be used.
    def __init__(self, index: int, *, has_trans):
        self.has_trans = has_trans
        self.trans_filepair = ("t%ds.txt" % index,
                               "t%de.txt" % index) if self.has_trans else None
        self.stage_filepair = ("s%ds.txt" % index, "s%de.txt" % index)
        self._trans_results = None
        self._stage_results = None
        self._calc_lock = RLock()

    def _calc_results(self):
        with self._calc_lock:
            if self._stage_results is not None:
                return
            self._trans_results = self._filepair_parse(
                *self.trans_filepair) if self.trans_filepair else dict()
            self._stage_results = self._filepair_parse(*self.stage_filepair)

    def query_result(self,
                     player,
                     qualify_time=None,
                     *,
                     default_trans_record=DNSRecord,
                     default_stage_record=DNSRecord) -> HibpEnduroTimeRecord:
        if self._stage_results is None:
            self._calc_results()
        trans, stage = (self._trans_results.get(player.playerno,
                                                default_trans_record),
                        self._stage_results.get(player.playerno,
                                                default_stage_record))

        return HibpEnduroTimeRecord(trans,
                                    stage,
                                    self._qualified(trans.result,
                                                    qualify_time),
                                    stage_config=self)

    def _qualified(self, t, qtime):
        if self.has_trans and isinstance(qtime, timedelta):
            if t in (NotAvailable, ):
                # means that this group do not use this transfer,
                # but needs to show its result as not available.
                return True
            if t in (DoNotStart, DidNotFinish):
                return False
            else:
                return t <= qtime
        return True

    def _filepair_parse(self, sfile, efile):
        """
        ret: player: HibpSingleTimeRecord
        """
        ret = {}
        sdict = self._load_hibp_raw_txt(sfile)
        edict = self._load_hibp_raw_txt(efile)
        for p, st in sdict.items():
            et = difft = DidNotFinish
            if p in edict:
                et = edict[p]
                difft = et - st
            ret[p] = HibpSingleTimeRecord(st, et, difft)
        return ret

    def _load_hibp_raw_txt(self, filename):
        """
        ret: dict of playerno:datetime
        """
        ret = dict()
        try:
            with open(RawFile(filename).fullpath) as f:
                for line in f:
                    items = line.strip().split()
                    h = HibpRawRecord(*items)
                    if h.playerno not in ret:
                        dt = datetime.fromtimestamp(int(
                            h.timestamp)).replace(microsecond=int(h.ms) * 1000)
                        ret[h.playerno] = dt
        except Exception as e:
            logger.error(e)
        finally:
            return ret


class GroupingStage():
    def __init__(self, stage: StageCommon, rank2score, qualify_time,
                 **query_result_kwargs):
        self.stage = stage
        self.rank2score = rank2score
        self.qualify_time = qualify_time
        self.query_result_kwargs = query_result_kwargs

    def __repr__(self):
        return f"{self.stage.trans_filepair},{self.stage.stage_filepair},{self.qualify_time}"

    @classmethod
    def list_factory(cls, stage_list: list, rank2score, qualify_time, **query_result_kwargs):
        return list(map(lambda x:cls(x, rank2score, qualify_time, **query_result_kwargs), stage_list))


class GroupingConfig():
    def __init__(self, name, index, stages):
        self.name = name
        self.index = index
        self.stages = stages


class Rank2ScoreFactory(object):
    def __init__(self, scorelist: list):
        self._scorelist = scorelist
        self._predefscores = len(scorelist)

    def __call__(self, rank: int) -> int:
        if rank < self._predefscores:
            return self._scorelist[rank]
        return 0

################################################################
# race configurations start from here

# Config stage info here.
AllStages = [
    StageCommon(1, has_trans=True),
    StageCommon(2, has_trans=False),
    StageCommon(3, has_trans=False),
]

# rank to score function
WomenScoreFunc = Rank2ScoreFactory([400, 350, 320] + list(range(300, 5, -10)) + [5, 1])
MenScoreFunc = Rank2ScoreFactory([500, 450, 420] + list(range(400, 145, -10)) + list(range(145, 49, -5)) + list(range(49, 0, -1)))

# timelimit
MenTimeLimit = timedelta(hours=2)
WomenTimeLimit = timedelta(hours=2)

# for all men bike stages
men_stages = GroupingStage.list_factory(AllStages, MenScoreFunc, MenTimeLimit)
# for sur-ron like e-moto bikes
emoto_stages = GroupingStage.list_factory(AllStages, MenScoreFunc, MenTimeLimit, default_trans_record=IGRecord)
# for women bike stages
women_stages = GroupingStage.list_factory(AllStages, WomenScoreFunc, WomenTimeLimit)

# groups config
# does not affect result if not exist
Groups = [
    GroupingConfig("荣誉领骑", 0, men_stages),
    GroupingConfig("轻蜂组", 8, emoto_stages),
    GroupingConfig("FREY组", 9, men_stages),
    GroupingConfig("女子组", 3, women_stages),
    GroupingConfig("男子组", 4, men_stages),
    GroupingConfig("大师A组", 6, men_stages),
    GroupingConfig("大师B组", 7, men_stages),
    GroupingConfig("精英组", 5, men_stages),
    GroupingConfig("青少年组", 2, men_stages),
    GroupingConfig("新人组", 1, men_stages),
]

# race configurations end
################################################################


def read_result():
    players_by_group = HibpPlayerMeta.load_player_meta()
    for group in Groups:
        player_results = dict()
        for stage in group.stages:
            # get and sort players
            for player in players_by_group[group.index]:
                if not player_results.get(player.playerno):
                    player_results[player.playerno] = HibpPlayerRecords(player)
                timerec = stage.stage.query_result(player, stage.qualify_time,
                                                   **stage.query_result_kwargs)
                player_results[player.playerno].stage_results.append(timerec)
                assert timerec.stage is not None, f"{player},{timerec},{stage}"
            # sort
            logger.debug(player_results.values())
            for rank, pr in enumerate(
                    sorted(player_results.values(),
                           key=lambda x: x.stage_results[-1])):
                sscore = stage.rank2score(
                    rank) if pr.stage_results[-1].scored else 0
                pr.stage_scores.append(sscore)
                pr.finalscore += sscore
        # calc total
        for rank, pr in enumerate(
                sorted(player_results.values(), reverse=True), 1):
            if pr.finalscore == 0:
                rank = "-"
            print(f"{group.name},{rank}," + str(pr))


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        RawFile.DIRPATH = sys.argv[1]
    read_result()

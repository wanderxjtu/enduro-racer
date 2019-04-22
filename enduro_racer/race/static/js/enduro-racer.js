/**
 * @format
 */
String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

angular
  .module("enduro-racer", [
    "ui.bootstrap",
    "ngRoute",
    "ngCookies",
    "angular.filter"
  ])
  .config([
    "$routeProvider",
    function($routeProvider) {
      $routeProvider.when("/", {
        templateUrl: STATIC + "partial/competitions.html",
      });
      $routeProvider.when("/all", {
        templateUrl: STATIC + "partial/competitions.html",
      });

      $routeProvider.when("/competition/:comp", {
        templateUrl: STATIC + "partial/competition.html",
      });

      $routeProvider.when("/competition/:comp/groups", {
        templateUrl: STATIC + "partial/groups.html",
      });

      $routeProvider.when("/competition/:comp/signup", {
        templateUrl: STATIC + "partial/signup.html",
      });

      $routeProvider.when("/new_admin", {
        templateUrl: STATIC + "partial/new_admin.html",
      });

      $routeProvider.when("/account", {
        templateUrl: STATIC + "partial/account.html",
      });

      $routeProvider.otherwise({
        redirectTo: "/"
      });
    }
  ])
  .config([
    "$compileProvider",
    function($compileProvider) {
      $compileProvider.directive("compileUnsafe", [
        "$compile",
        function($compile) {
          return function(scope, element, attrs) {
            scope.$watch(
              function(scope) {
                // watch the 'compile' expression for changes
                return scope.$eval(attrs.compileUnsafe);
              },
              function(value) {
                // when the 'compile' expression changes
                // assign it into the current DOM element
                element.html(value);

                // compile the new DOM and link it to the current
                // scope.
                $compile(element.contents())(scope);
              }
            );
          };
        }
      ]);
    }
  ])
  .config([
    "$httpProvider",
    function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
  ])
  .config([
    "$locationProvider",
    function($locationProvider) {
      $locationProvider.hashPrefix('');
    }
  ])
  .directive("ngSetFocus", [
    "$timeout",
    function($timeout) {
      return function(scope, element, attrs) {
        scope.$watch(
          attrs.ngSetFocus,
          function(newValue) {
            if (newValue) {
              $timeout(function() {
                element[0].focus();
              });
            }
          },
          true
        );
      };
    }
  ])
  .run([
    "$rootScope",
    "$location",
    "$routeParams",
    function($rootScope, $location, $routeParams) {
      $rootScope.$on("$routeChangeSuccess", function(scope, current, pre) {
        $rootScope.location = {
          path: $location.path()
        };
      });
    }
  ])
  .filter("genderFromInt", function() {
    return function(input) {
      if (input == 0) {
        return "female";
      }
      return "male";
    };
  })
  .filter("startFrom", function() {
    return function(input, start) {
      start = parseInt(start, 10);
      return input.slice(start);
    };
  })
  .directive("visible", [
    "$parse",
    function($parse) {
      return {
        restrict: "A",
        link: function(scope, element, attrs) {
          scope.$watch(
            function() {
              return $parse(attrs.visible)(scope);
            },
            function(visible) {
              element.css("visibility", visible ? "visible" : "hidden");
            }
          );
        }
      };
    }
  ])
  .controller("BaseCtrl", [
    "$rootScope",
    "$location",
    function($rootScope, $location) {
      $rootScope._ = _;
      $rootScope.USER = USER;
      $rootScope.ROOT = ROOT;
      $rootScope.API = ROOT + "api/";
      $rootScope.ADMIN = ROOT + "admin/";
      $rootScope.IS_ADMIN = IS_ADMIN;
      $rootScope.NEED_ADMIN = NEED_ADMIN;
      $rootScope.STATIC = STATIC;
      $rootScope.PARTIAL = STATIC + "partial/";
      $rootScope.SECURE_COOKIE = SECURE_COOKIE;
      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }

      $rootScope.getDevice = function() {
        var envs = ["xs", "sm", "md", "lg"];

        var el = document.createElement("div");
        var body = document.getElementsByTagName("body")[0];
        body.appendChild(el);

        for (var i = envs.length - 1; i >= 0; i--) {
          var env = envs[i];

          el.setAttribute("class", "hidden-" + env);
          if (el.offsetWidth === 0 && el.offsetHeight === 0) {
            el.remove();
            return env;
          }
        }
      };

      $rootScope.device = $rootScope.getDevice();
      $rootScope.getWidth = function() {
        return window.innerWidth;
      };
      $rootScope.$watch($rootScope.getWidth, function(newValue, oldValue) {
        if (newValue != oldValue) {
          $rootScope.device = $rootScope.getDevice();
        }
      });
      window.onresize = function() {
        $rootScope.$apply();
      };
    }
  ])
  .controller("NavbarCtrl", [
    "$scope",
    function($scope) {
      $scope.navCollapsed = true; //$scope.device === "xs";
      $scope.options = [];
    }
  ])
  .controller("IndexCtrl", [
    "$scope",
    "$http",
    "$location",
    "$cookies",
    function($scope, $http, $location, $cookies) {
      $scope.$cookies = $cookies;
      $scope.competitions = null;
      $scope.showOpen = $location.path();
      $scope.pageSize = 10;
      $scope.maxSize = 8;
      $scope.currentPage = 1;
      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }


      $http
        .get($scope.API + "competitions/", { params: { showOpen: !$scope.showOpen.endsWith("all")} })
        .then(function(response) {
          $scope.competitions = response.data.competitions;
        },function(error) {
          console.error("Fetching competitions failed");
        });

      $scope.showCompetition = function(comp) {
        $location.path("/competition/" + comp);
      };
      $scope.showCompetitionGroup = function(comp) {
        $location.path("/competition/" + comp + "/groups/");
      };
      $scope.showCompetitionSignup = function(comp) {
        $location.path("/competition/" + comp + "/signup/");
      };
    }
  ])
  .controller("CompetitionCtrl", [
    "$scope",
    "$http",
    "$route",
    "$cookies",
    "$location",
    function($scope, $http, $route, $cookies, $location) {
      $scope.$cookies = $cookies;
      $scope.comp_uniname = $route.current.params.comp

      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }

      $http
        .get($scope.API + "competition/" + $scope.comp_uniname)
        .then(function(response) {
          $scope.comp = response.data.object;
        },function(error) {
          console.error("Fetching competition failed");
        });

      $scope.showCompetitionGroup = function(comp) {
        $location.path("/competition/" + comp + "/groups/");
      };
      $scope.showCompetitionSignup = function(comp) {
        $location.path("/competition/" + comp + "/signup/");
      };
      $scope.showCompetitionDetail = function(comp) {
        $location.path("/competition/" + comp);
      };
    }
  ])
  .controller("CompetitionSignupCtrl", [
    "$scope",
    "$http",
    "$route",
    "$cookies",
    "$window",
    "$location",
    function($scope, $http, $route, $cookies, $window, $location) {
      $scope.$cookies = $cookies;
      $scope.comp_uniname = $route.current.params.comp;
      $scope.allregions = $window.alpha3regions;
      $scope.today = new Date();

      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }

      // need User -> RacerInfo
      // need teamList
      $http.get($scope.API + "teams/")
      .then(function(response) {
          $scope.teams = response.data.teams;
      },function(error) {
          console.error("Fetching competition failed");
      });;

      $scope.signUp = function(racer) {
        $http.post($scope.API + "competition/" + $scope.comp_uniname + "/signup/", racer)
        .then(function(response) {
          $scope.signup_result = response.data.object;
        },function(error) {
          $scope.signup_result = {"success": false, "message": "提交失败，请再试一次"}
          console.error("Signup Error");
        });
      };
    }
  ])
  .controller("GroupsCtrl", [
    "$scope",
    "$http",
    "$route",
    "$cookies",
    "$window",
    function($scope, $http, $route, $cookies, $window) {
      $scope.$cookies = $cookies;
      $scope.comp_uniname = $route.current.params.comp
      $scope.regionsemoji = $window.alpha3emoji;

      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }

      $http
        .get($scope.API + "competition/" + $scope.comp_uniname + "/group/")
        .then(function(response) {
          $scope.groups = response.data.groups;
        },function(error) {
          console.error("Fetching competition failed");
        });
    }
  ])
  .controller("LoginCtrl", [
    "$scope",
    "$http",
    "$window",
    "$location",
    function($scope, $http, $window, $location) {
      $scope.error = false;
      $scope.loggingIn = false;

      $scope.token = $location.search().token;
      if ($scope.token) {
        $scope.useToken = true;
        $scope.startWithToken = true;
      }
      if ($window.location.protocol != "https:" && SECURE_COOKIE) {
        $scope.secureCookieError = true;
      }

      $scope.toggleTokenRegistration = function() {
        $scope.useToken = !$scope.useToken;
      };

      $scope.submit = function(username, password) {
        $scope.loggingIn = true;
        var data = {
          username: username,
          password: password
        };
        $http
          .post(ROOT + "login", data)
          .success(function(data, status, headers, config) {
            $scope.loggingIn = false;
            $scope.error = false;
            $window.location = data.next;
          })
          .error(function(data, status, headers, config) {
            $scope.loggingIn = false;
            $scope.error = true;
            $scope.errorMsg = "Username or password invalid";
          });
      };

      $scope.register = function(username, password) {
        var data = {
          username: username,
          password: password
        };
        $http
          .put(ROOT + "login", data)
          .success(function(data, status, headers, config) {
            $scope.error = false;
            $scope.registered = username;
          })
          .error(function(data, status, headers, config) {
            $scope.error = true;
            if (status === 400) {
              $scope.errorMsg =
                data.message == null
                  ? "Error during registration"
                  : data.message;
            } else if (status === 403) {
              $scope.errorMsg = "Registration has been disabled";
            } else {
              $scope.errorMsg = "Error during registration: " + data.message;
            }
          });
      };

      $scope.tokenRegister = function(token, password) {
        var data = {
          token: token,
          password: password
        };
        $scope.registering = true;
        $http
          .put(ROOT + "tokenRegister", data)
          .success(function(data, status, headers, config) {
            $scope.error = false;
            $scope.registering = false;
            $window.location = data.next;
          })
          .error(function(data, status, headers, config) {
            $scope.error = true;
            $scope.registering = false;
            if (status === 400) {
              $scope.errorMsg =
                data.message == null
                  ? "Error during registration"
                  : data.message;
            } else {
              $scope.errorMsg = "Error during registration: " + data.message;
            }
          });
      };
    }
  ])
  .controller("NewAdminCtrl", [
    "$scope",
    "$http",
    "$location",
    function($scope, $http, $location) {
      $scope.register = function(username, password) {
        var data = {
          username: username,
          password: password
        };
        $http
          .put(ROOT + "login", data)
          .success(function(data, status, headers, config) {
            window.location = ROOT;
          })
          .error(function(data, status, headers, config) {
            alert("Error registering admin user");
          });
      };
    }
  ])
  .controller("AccountCtrl", [
    "$scope",
    "$http",
    function($scope, $http) {
      $scope.changePassword = function(oldPassword, newPassword) {
        if (
          !oldPassword ||
          !newPassword ||
          oldPassword.length === 0 ||
          newPassword.length === 0
        ) {
          $scope.passError = "Password cannot be blank!";
          return;
        }
        var data = {
          new_password: newPassword,
          old_password: oldPassword
        };
        $scope.changingPasswordNetwork = true;
        $http
          .post($scope.API + "user/password", data)
          .success(function(data, status, headers, config) {
            $scope.changingPasswordNetwork = false;
            $scope.changingPassword = false;
            $scope.newPassword = "";
            $scope.oldPassword = "";
            $scope.passError = null;
          })
          .error(function(data, status, headers, config) {
            $scope.changingPasswordNetwork = false;
            $scope.passError = "Invalid password!";
          });
      };
    }
  ]);

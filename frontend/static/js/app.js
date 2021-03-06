var myApp = angular.module('myApp', ["ngRoute"]);

myApp.controller('mainCtrl', ['$scope', '$rootScope', function ($scope, $rootScope) {

    $scope.selectedC = "";

    $scope.selectedSBT = "";
    $scope.selectedUp = "";

    $scope.info = "image-info";
    $scope.exploreMenu = "Explore";
    $scope.explore_var;
    $scope.imageList;

    $scope.clickExplore = function () {
        if (!$scope.explore_var) {
            $scope.selectedC = "selected";
            $scope.exploreMenu = "Explore!";
            $scope.explore_var = !$scope.explore_var;
        } else {
            $scope.selectedC = "";
            $scope.exploreMenu = "Explore";
            $scope.explore_var = !$scope.explore_var;
        }
    }

    $scope.disableExplore = function () {
        $scope.selectedC = "";
        $scope.exploreMenu = "Explore";
        $scope.explore_var = false;
    }

    $scope.clickSBT = function(){
        ($scope.selectedSBT ? $scope.selectedSBT = "" : $scope.selectedSBT = "selected", $scope.selectedUp = "");

    }

    $scope.clickUpload_ = function(){
        ($scope.selectedUp ? $scope.selectedUp = "" : $scope.selectedUp = "selected", $scope.selectedSBT = "");
    }




    $scope.moreImages = function () {
        console.log("emitting more images");
        $rootScope.$emit("moreImages", {});

    }

}])

myApp.config(function ($routeProvider) {
    $routeProvider
        .when("/", {
            templateUrl: "list_images.htm"
        })
        .when("/search", {
            templateUrl: "search.htm"
        });
    /*.when("/upload", {
        templateUrl : "upload.htm"
    });*/
});

myApp.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;

            element.bind('change', function () {
                scope.$apply(function () {
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);


myApp.service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function (obj, uploadUrl, $scope) {
        var fd = new FormData();
        for (key in obj) {
            fd.append(key, obj[key]);
        }
        fd.append('quote', "");
        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        }).then(function (response) {
            $scope.callBack(response);
        }, function (response) {
            console.log(response.data);
            alert(response.data);
        })
    }
}]);

myApp.controller('myCtrl', ['$scope', 'fileUpload', '$rootScope', function ($scope, fileUpload, $rootScope) {

    $scope.count = 0;

    $scope.$watch('myFile', function () {
        if ($scope.count > 0) {
            console.log("uploading");
            console.log($scope.count);
            $scope.uploadFile();
        }

        $scope.count++;

    });

    $scope.clickUpload = function () {
        document.getElementById('myInput').click();
    };

    $scope.uploadFile = function () {
        var file = $scope.myFile;
        if (file != undefined) {
            var title = $scope.myTitle;
            var obj = {image: file, title: title};
            console.log('file is ');
            console.dir(file);
            var uploadUrl = "/api/image_upload/";

            fileUpload.uploadFileToUrl(obj, uploadUrl, $scope);
        }
    };


    $scope.callBack = function (response) {
        $scope.done = response.data;
        console.log("calling back");
        console.log($scope.done)
        $rootScope.$emit("Explore", $scope.done.pk);
        $scope.myTitle = "";
    }

}]);

myApp.controller('queryCtrl', ['$scope', 'fileUpload', '$rootScope', function ($scope, fileUpload, $rootScope) {

    $scope.count = 0;

    $scope.clickUpload = function () {
        document.getElementById('mySearch').click();
    };

    $scope.$watch('myFile', function () {
        if ($scope.count > 0) {
            console.log("uploading");
            console.log($scope.count);
            $scope.uploadFile();
        }

        $scope.count++;

    });

    $scope.uploadFile = function () {
        var file = $scope.myFile;
        if (file != undefined) {
            var obj = {myfile: file};
            console.log('file is ');
            console.dir(file);
            var uploadUrl = "/api/query_up/";
            fileUpload.uploadFileToUrl(obj, uploadUrl, $scope);
        }
    };

    $scope.callBack = function (response) {
        var imgName = response.data;
        console.log("calling back - search controller");
        console.log(imgName)
        $rootScope.$emit("Explore", imgName);
    }

}]);


//Image List Controller
myApp.controller('listCtrl', ['$scope', '$http', '$rootScope', '$window', function ($scope, $http, $rootScope, $window) {


    $scope.openInNewTab = function (link) {
        console.log("open in new tab");
        $window.open(link, '_blank');
    }

    $scope.reload = function () {
        $window.location.reload();

    }

    $http.get("/api/image_list/", {cache: true}).then(function (response) {
        //console.log("image_list")
        $scope.imageList = response.data.results;
        console.log($scope.imageList);
    }, function (response) {
    })


    $scope.moreImages = function () {
        $scope.exploring = false;
        $http.get("/api/image_list/").then(function (response) {
            console.log("in more images function")
            /*for(var i = 0; i < response.data.results.length; i++){
                console.log(response.data.results[i]);
                $scope.imageList.unshift(response.data.results[i]);
            }*/
            $scope.imageList = response.data.results.concat($scope.imageList);
            if ($scope.imageList.length > 60) {
                $scope.imageList.splice(60);
            }

        }, function (response) {
        })

    }

    $rootScope.$on("moreImages", function (event, data) {
        console.log("i'm on air");
        console.log("charging more images");
        $scope.moreImages();
    })

    $rootScope.$on("Explore", function (event, data) {
        console.log("i'm on air");
        console.log(data);
        $scope.explore(data);
    });

    $rootScope.$on("retrieveByTag", function (event, data) {
        console.log("i'm on air");
        console.log(data);
        $scope.retrieveByTag(data);
    });

    $scope.retrieveByTag = function (tag) {
        $http.get("/api/retrieve_by_tag/" + tag + "/", {cache: true}).then(function (response) {
            //console.log("image_list")
            $scope.imageList = response.data.results;
            console.log($scope.imageList);
        }, function (response) {
        })
        $scope.showOverlay = false;
        $scope.disableExplore();
        $scope.exploring = false;
    }


    $scope.explore = function (key) {
        console.log("exploring ");
        console.log(key);
        var address;
        var cache;
        if (key != $scope.pages.key) {
            $scope.pages.current = 1;
        }
        if (typeof key == "string") {
            address = "/api/query_get/" + key + "/" + "?page=" + $scope.pages.current;
        } else {
            address = "/api/explore/" + key + "/" + "?page=" + $scope.pages.current;

        }
        $http.get(address, {cache: false}).then(function (response) {
            //response handling begin
            $scope.imageList = response.data.results;
            //console.log($scope.imageList);
            $scope.exploring = true;
            if (key != $scope.pages.key) {
                $scope.pages.current = 1;
                $scope.pages.key = key;
                $scope.pages.allPages = [];
                for (i = 0; i < response.data.total_pages; i++)
                    $scope.pages.allPages.push(i + 1);
            }
            //response handling end
        }, function (response) {
        });

        $scope.disableExplore()

    }

    $scope.pages = {
        current: 1,
        key: null,
        allPages: []
    };

    $scope.changePage = function (p) {
        if (p <= $scope.pages.allPages.length && p > 0) {
            console.log(p + "changing page");
            console.log($scope.pages.allPages);
            $scope.pages.current = p;
            $scope.explore($scope.pages.key);
        }
    }

    $scope.isCurrent = function (numPage) {
        if (numPage == $scope.pages.current) {
            return "w3-bar-item w3-button-black";
        } else {
            return "w3-bar-item w3-button w3-hover-black";
        }
    }

    $scope.isVisible = function (numPage) {
        var numPageToDisplay = 9;
        if (Math.floor((numPage - 1) / numPageToDisplay) == Math.floor(($scope.pages.current - 1) / numPageToDisplay)) {
            return true;
        }
        return false;
    }

    $scope.showOverlay = false;
    $scope.imageToShow;
    $scope.explore_var;

    $scope.showImage = function (imageToShow) {
        if(!$scope.explore_var) {
            $scope.showOverlay = true;
            $scope.imageToShow = imageToShow;
        }
        else{
            $scope.pages.current = 1;
            $scope.explore(imageToShow.pk);
        }
    }

}])


myApp.controller("tagCtrl", ["$scope", '$http', '$rootScope', function ($scope, $http, $rootScope) {

    $http.get("/api/retrieve_tags/", {cache: true}).then(function (response) {
        //console.log("image_list")
        $scope.all_tags = response.data;
        console.log($scope.all_tags);
    }, function (response) {
    })


    $scope.search = function (tag) {
        if ($scope.all_tags.includes(tag)) {
            $rootScope.$emit("retrieveByTag", tag);
            $scope.error = "";
        } else {
            $scope.error = "There aren't pictures with " + (tag ? '"' + tag + '"' : "that") + " tag. ";
            var nn = getNearestWord(tag);
            $scope.error += "Maybe do you mean '" + nn +"'?";
            $scope.myTag = nn;
        }
    }

    $scope.myFunct = function (keyEvent) {
        if (keyEvent.which === 13){
            $scope.search($scope.myTag)
        }
    }

    function getNearestWord(tag){
        tags = $scope.all_tags;
        distance_vector = [];
        for(i=0; i < tags.length; i++){
            dist = levenshtein_distance_a(tag, tags[i]);
            distance_vector.push(dist);
        }
        $scope.min = Math.min.apply(null, distance_vector);

        result_index = distance_vector.findIndex(function(el){return el <= $scope.min});
        return tags[result_index];

    }

    function levenshtein_distance_a (a, b) {
    if(a.length == 0) return b.length;
    if(b.length == 0) return a.length;

    var matrix = [];

    // increment along the first column of each row
    var i;
    for(i = 0; i <= b.length; i++){
      matrix[i] = [i];
    }

    // increment each column in the first row
    var j;
    for(j = 0; j <= a.length; j++){
      matrix[0][j] = j;
    }

    // Fill in the rest of the matrix
    for(i = 1; i <= b.length; i++){
      for(j = 1; j <= a.length; j++){
        if(b.charAt(i-1) == a.charAt(j-1)){
          matrix[i][j] = matrix[i-1][j-1];
        } else {
          matrix[i][j] = Math.min(matrix[i-1][j-1] + 1, // substitution
                                  Math.min(matrix[i][j-1] + 1, // insertion
                                           matrix[i-1][j] + 1)); // deletion
        }
      }
    }

    return matrix[b.length][a.length];
  }

}])



























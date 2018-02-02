var myApp = angular.module('myApp', ["ngRoute"]);

myApp.controller('mainCtrl', function($scope){
    $scope.selectedA = "selected";
    $scope.selectedB = "";
    $scope.selectedC = "";
    $scope.selectedD = "";
    $scope.info = "image-info";
    
    $scope.deselectAll = function(){
        $scope.selectedA = "";
        $scope.selectedB = "";
        $scope.selectedD = "";
    }
    
    $scope.clickC = function(){
        if($scope.explore_var){
            $scope.selectedC = "selected";
        }else{
            $scope.selectedC = "";
        }
        
    }
})

myApp.config(function($routeProvider) {
    $routeProvider
    .when("/", {
        templateUrl : "list_images.htm"
    })
    .when("/search", {
        templateUrl : "search.htm"
    });
    /*.when("/upload", {
        templateUrl : "upload.htm"
    });*/
});

myApp.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

myApp.service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function(obj, uploadUrl, $scope){
        var fd = new FormData();
        for(key in obj){
            fd.append(key, obj[key]);
        }
        fd.append('quote', "");
        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        }).then(function(response) {
            $scope.callBack(response);
    }, function(response){
            console.log(response.data);
            alert(response.data);
        })
    }
}]);

myApp.controller('myCtrl', ['$scope', 'fileUpload', '$rootScope', function($scope, fileUpload, $rootScope){
    
    $scope.uploadFile = function(){
        var file = $scope.myFile;
        var title = $scope.myTitle;
        var obj = {image:file, title:title};
        console.log('file is ' );
        console.dir(file);
        var uploadUrl = "/api/image_upload/";
        fileUpload.uploadFileToUrl(obj, uploadUrl, $scope);
    };
    
    
    
    $scope.callBack = function(response){
            $scope.done = response.data;
            console.log("calling back");
            console.log($scope.done)
            $rootScope.$emit("Explore", $scope.done.pk);
    }
    
}]);

myApp.controller('queryCtrl', ['$scope', 'fileUpload', '$rootScope', function($scope, fileUpload, $rootScope){
    
    $scope.uploadFile = function(){
        var file = $scope.myFile;
        var obj = {myfile:file};
        console.log('file is ' );
        console.dir(file);
        var uploadUrl = "/api/query_up/";
        fileUpload.uploadFileToUrl(obj, uploadUrl, $scope);
    };
    
    $scope.callBack = function(response){            
        var imgName = response.data;
        console.log("calling back - search controller");
        console.log(imgName)
        $rootScope.$emit("Explore", imgName);
    }
  
}]);




//Image List Controller
myApp.controller('listCtrl', ['$scope', '$http', '$rootScope', '$window', function($scope, $http, $rootScope, $window){
    
    $scope.openInNewTab = function(link){
        console.log("open in new tab");
        $window.open(link, '_blank');
    }
    
    $scope.reload = function(){
        $window.location.reload();

    }
    
    $http.get("/api/image_list/", {cache: true}).then(function(response){
        //console.log("image_list")
        $scope.imageList = response.data.results;
        
    }, function(response){
    })
    
    $rootScope.$on("Explore", function(event, data){
        console.log("i'm on air");
        console.log(data);
        $scope.explore(data);
    });    

    
    $scope.explore = function(key){
        console.log("exploring ");
        console.log(key);
        var address;
        if(typeof key == "string"){
                address = "/api/query_get/" + key + "/" + "?page=" + $scope.pages.current;
         }else{
                address = "/api/explore/" + key + "/" + "?page=" + $scope.pages.current;
         }
        $http.get(address, {cache: true}).then(function(response){
        //response handling begin    
        $scope.imageList = response.data.results;
        //console.log($scope.imageList);
        $scope.exploring = true;
        if(key != $scope.pages.key){
        $scope.pages.current = 1;
        $scope.pages.key = key;
        $scope.pages.allPages = [];
        for(i = 0; i < response.data.total_pages; i++)
            $scope.pages.allPages.push(i + 1);
        }
        //response handling end  
    }, function(response){
    });
    }
    
    $scope.pages = {  
        current:1,
        key:null,
        allPages:[]
    };
    
    $scope.changePage= function(p){
        if(p <= $scope.pages.allPages.length && p > 0 ){
            console.log(p + "changing page");
            console.log( $scope.pages.allPages );
            $scope.pages.current = p;
            $scope.explore($scope.pages.key);
        }
    }
    
    $scope.isCurrent = function(numPage){
        if(numPage == $scope.pages.current){
            return "w3-bar-item w3-button-black";
        }else{
            return "w3-bar-item w3-button w3-hover-black";
        }
    }
    
    $scope.isVisible = function(numPage){
        var numPageToDisplay = 9;
        if( Math.floor( (numPage - 1)/numPageToDisplay ) ==  Math.floor( ($scope.pages.current - 1)/numPageToDisplay ) ){
            return true;  
           }
        return false;
    }

}])
/*
0 1 2 3 4 5 6 7| 8 9 10 11 12 13 14 15| 16

      0        |            1         |
*/































var myApp = angular.module('myApp', ["ngRoute"]);

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
            $scope.done = response.data;
            console.log($scope.done);
    });
    }
}]);

myApp.controller('myCtrl', ['$scope', 'fileUpload', function($scope, fileUpload){
    
    $scope.uploadFile = function(){
        var file = $scope.myFile;
        var title = $scope.myTitle;
        var obj = {image:file, title:title};
        console.log('file is ' );
        console.dir(file);
        var uploadUrl = "/api/image_upload/";
        fileUpload.uploadFileToUrl(obj, uploadUrl, $scope);
    };
    
}]);

myApp.controller('queryCtrl', ['$scope', 'fileUpload', function($scope, fileUpload){
    
    $scope.uploadFile = function(){
        var file = $scope.myFile;
        var obj = {myfile:file};
        console.log('file is ' );
        console.dir(file);
        var uploadUrl = "/api/query/";
        fileUpload.uploadFileToUrl(obj, uploadUrl, $scope);
        $scope.Search = true;
    };
    
}]);




//Image List Controller
myApp.controller('listCtrl', function($scope, $http){
    
    $http.get("/api/image_list/",  { cache: true }).then(function(response){
        $scope.imageList = response.data;
    }, function(response){
    })

} )


































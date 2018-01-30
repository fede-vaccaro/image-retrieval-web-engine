myApp.factory('Images', function($resource) {
  return $resource('/api/image_list/')
});

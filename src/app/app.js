MathJax.Hub.Config({
	tex2jax: {
	  inlineMath: [['$','$'], ['\\(','\\)']],
	  processEscapes: true
	}
});

var SearchApp =
  angular.module('TopicModelSearchApp', ['ngRoute', 'ui.slider'])
  .config(function($interpolateProvider) {
      $interpolateProvider.startSymbol('{[');
      $interpolateProvider.endSymbol(']}');
  })
  .config(function($routeProvider){
    $routeProvider.when('/', {
      controller: 'SearchController',
      templateUrl: 'src/app/views/search.html'
    })
  });

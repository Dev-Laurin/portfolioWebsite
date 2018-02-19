var app = angular.module('app', ['ngRoute']); 

app.config(function($routeProvider){
	$routeProvider

		//home page
		.when('/', {
			templateUrl : 'html/pages/home.html',
			controller : 'mainController'
		})

		.when('/about', {
			templateUrl : 'html/pages/about.html',
			controller : 'aboutController'
		}) 

		.when('/contact', {
			templateUrl : 'html/pages/contact.html',
			controller : 'contactController'
		});
});

app.controller('mainController', function($scope){

}); 

app.controller('aboutController', function($scope){

}); 

app.controller('contactController', function($scope){

}); 
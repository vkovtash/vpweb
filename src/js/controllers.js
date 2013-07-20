'use strict';

/* Controllers */

function ShowListCtrl($scope, $http) {
  $http.get('shows').success(function(data) {
  	$scope.shows = data.Shows;
	});
}

function ShowDetailCtrl($scope, $routeParams, Show) {
	$scope.show = Show.get({showId: $routeParams.showId});
}
'use strict';

/* App Module */

angular.module('vpweb', ['vpwebServices','vpwebFilters']).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/shows', {templateUrl: 'src/partials/show-list.html',   controller: ShowListCtrl}).
      when('/shows/:showId', {templateUrl: 'src/partials/show-detail.html', controller: ShowDetailCtrl}).
      otherwise({redirectTo: '/shows'});
}]);

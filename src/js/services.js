'use strict';

/* Services */

angular.module('vpwebServices', ['ngResource']).
    factory('Show', function($resource){
  return $resource('shows/:showId', {showId:'@showId'}, {
    get: {method:'GET'},
    save: {method:'POST'}
  });
});
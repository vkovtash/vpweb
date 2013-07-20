'use strict';

/* Filters */

angular.module('vpwebFilters', []).filter('length', function() {
  return function(input) {
    return input.length;
  };
});
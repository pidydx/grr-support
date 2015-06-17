(function(){

	var sets = [
		{ 
			id: 1,
			name: "Set 1", rows: 42
		},
		{ 
			id: 2,
			name: "Set 2", rows: 42
		}
	];

	function getRows(type,id) {
		return 40;
	}

	var app = angular.module('tip', ['ui.bootstrap']);

	app.controller("DisplayController", function($scope, $http){

		$http({method: "GET", url:'http://localhost:8000/ti/datasources/?format=json'}).success(function(data) {
        	for (var i in data.results) {
        		data.results[i].rows = getRows();
        		data.results[i].selected = false;
        		data.results[i].tab = false;
        		data.results[i].rowdata = []
        	}
        	$scope.dataSourceList = data.results;
    	});

		$http({method: "GET", url:'http://localhost:8000/ti/tags/?format=json'}).success(function(data) {
    	    for (var i in data.results) {
    			data.results[i].rows = getRows();
    			data.results[i].selected = false;
        		data.results[i].tab = false;
        		data.results[i].rowdata = []
    		}
    		$scope.tagList = data.results;
    	});

		$scope.setList = []; //start null

		$scope.currentDataSourceId = 0;
		$scope.currentSetId = 0;
		$scope.currentTagId = 0;

		$scope.$watch('tagList', function(newVal, oldVal) {
			for (var i = 0; i < newVal.length; i++) {
				if (newVal[i].selected === false && oldVal[i].selected === true){
					$scope.tagList[i].tab = false;
					$scope.tagList[i].rows = 1;
				}
    		}
   		},true);

   		$scope.$watch('setList', function(newVal, oldVal) {
			for (var i = 0; i < newVal.length; i++) {
				if (newVal[i].selected === false && oldVal[i].selected === true){
					$scope.setList[i].tab = false;
				}
    		}
   		},true);

   		$scope.$watch('dataSourceList', function(newVal, oldVal) {
			for (var i = 0; i < newVal.length; i++) {
				if (newVal[i].selected === false && oldVal[i].selected === true){
					$scope.dataSourceList[i].tab = false;
				}
    		}
   		},true);
	});
})();

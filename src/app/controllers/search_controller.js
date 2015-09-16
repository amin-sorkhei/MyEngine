SearchApp.controller('SearchController', function(API, $scope){
  var keywordSelectionHistory = {};
  var iterationSelections = [];

  $scope.showSearchInput = true;
  $scope.settings = {
    topicCount: 10,
    keywordCount: 10
  };

  $scope.toggleShowSettings = function(){
      $scope.showSettings = !$scope.showSettings;
  }

  $scope.newQuery = function(){
    $scope.isSearching = false;
    $scope.showSearchInput = true;
    $scope.showOptionButtons = false;
    $scope.queryKeywords = '';
    $scope.searchKeywords = '';

    window.scrollTo(0,0);
  }

  $scope.nextIterationIsDisabled = function(){
    if($scope.isLoading){
      return true;
    }

    var selectedArticles = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.articles);
      }, [])
      .where({ selected: true })
      .value();

    var selectedKeywords = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.keywords);
      }, [])
      .where({ selected: true })
      .value();

    return ( selectedArticles.length + selectedKeywords.length ) == 0;
  }

  $scope.nextIteration = function(){
    window.scrollTo(0, 0);

    $scope.isLoading = true;

    console.log(iterationSelections);

    var selectionIds = _.map(iterationSelections, function(selection){ return selection.id });

    API.next({ selections: selectionIds }).then(function(results){
      rawTopics = results.data;
      $scope.topics = [];

      for(topicName in rawTopics){
        rawTopics[topicName].keywords.forEach(function(keyword){
          if(keywordSelectionHistory[keyword.label]){
            keyword.selected = true;
          }
        });

        $scope.topics.push({
          topic: topicName,
          keywords: rawTopics[topicName].keywords,
          articles: rawTopics[topicName].articles
        })
      }

      $scope.isLoading = false;
    });
  }

  $scope.abstractKeywordClicked = function(keyword, topicName){
    var targetTopic = _.find($scope.topics, function(topic){
      return topic.topic == topicName
    });

    var targetKeyword = _.find(targetTopic.keywords, function(k){
      return k.label == keyword;
    });

    $scope.toggleKeyword(targetKeyword);

    return targetKeyword;
  }

  $scope.search = function(){
    $scope.searchKeywords = $scope.queryKeywords;
    $scope.showOptionButtons = true;
    $scope.showSearchInput = false;
    $scope.isSearching = true;
    $scope.isLoading = true;

    API.search({ keywords: $scope.queryKeywords, topicCount: $scope.settings.topicCount, keywordCount: $scope.settings.keywordCount }).then(function(results){
      rawTopics = results.data;
      $scope.topics = [];

      for(topicName in rawTopics){
        $scope.topics.push({
          topic: topicName,
          keywords: rawTopics[topicName].keywords,
          articles: rawTopics[topicName].articles
        })
      }

      $scope.isLoading = false;
    });
  }

  $scope.toggleKeyword = function(keyword){
    keyword.selected = !keyword.selected;

    if(keyword.selected){
      keywordSelectionHistory[keyword.label] = true;
      iterationSelections.push(keyword);
    }else{
      delete keywordSelectionHistory[keyword.label]
      _.remove(iterationSelections, function(selection){ return selection.id == keyword.id });
    }
  }

  $scope.toggleArticle = function(article){
    article.selected = !article.selected;

    if(article.selected){
      iterationSelections.push(article);
    }else{
      _.remove(iterationSelections, function(selection){ return selection.id == article.id });
    }
  }
});

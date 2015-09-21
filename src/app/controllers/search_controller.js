SearchApp.controller('SearchController', function(API, $scope){
  var keywordSelectionHistory = {};
  var articleSelectionHistory = {};
  var iterationSelections = [];

  function setSelections(){
    $scope.topics.forEach(function(topic){
      topic.keywords.forEach(function(keyword){
        keyword.selected = keywordSelectionHistory[keyword.label];
      });

      topic.articles.forEach(function(article){
        article.selected = articleSelectionHistory[article.id]
      });
    });
  }

  $scope.showSearchInput = true;
  $scope.settings = {
    topicCount: 10,
    keywordCount: 10
  };

  $scope.toggleShowSettings = function(){
      $scope.showSettings = !$scope.showSettings;
  }

  $scope.toggleAbstract = function(article){
    article.showAbstract = !article.showAbstract
  }

  $scope.chooseAuthor = function(author){
    $scope.chosenAuthor = author;
    $scope.showAuthor = true;
  }

  $scope.hideAuthor = function(){
    $scope.showAuthor = false;
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

    var selectedArticlesCount = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.articles);
      }, [])
      .where({ selected: true })
      .value()
      .length;

    var selectedKeywordsCount = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.keywords);
      }, [])
      .where({ selected: true })
      .value()
      .length;

    var selectedAuthorArticlesCount = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.articles);
      }, [])
      .reduce(function(all, article){
        return all.concat(article.authors)
      }, [])
      .reduce(function(all, author){
        return all.concat(author.articles)
      }, [])
      .where({ selected: true })
      .value()
      .length;

    return ( selectedArticlesCount + selectedKeywordsCount + selectedAuthorArticlesCount ) == 0;
  }

  $scope.nextIteration = function(){
    window.scrollTo(0, 0);

    $scope.isLoading = true;

    var selectionIds = _.map(iterationSelections, function(selection){ return selection.id });

    API.next({ selections: selectionIds }).then(function(results){
      $scope.topics = results.data;

      setSelections();

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
    keywordSelectionHistory = {};
    articleSelectionHistory = {};

    $scope.searchKeywords = $scope.queryKeywords;
    $scope.showOptionButtons = true;
    $scope.showSearchInput = false;
    $scope.isSearching = true;
    $scope.isLoading = true;

    API.search({ keywords: $scope.queryKeywords, topicCount: $scope.settings.topicCount, keywordCount: $scope.settings.keywordCount }).then(function(results){
      $scope.topics = results.data;
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

    articleSelectionHistory[article.id] = article.selected;

    if(article.selected){
      iterationSelections.push(article);
    }else{
      _.remove(iterationSelections, function(selection){ return selection.id == article.id });
    }
  }
});

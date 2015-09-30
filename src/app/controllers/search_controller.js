SearchApp.controller('SearchController', function(API, $scope){
  var keywordSelectionHistory = {};
  var articleSelectionHistory = {};
  var iterationSelections = [];

  function setSelections(){
    $scope.topics.forEach(function(topic){
      topic.articlesDisplaying = 2;
      topic.keywordsDisplaying = $scope.settings.keywordCount;

      topic.keywords.forEach(function(keyword){
        keyword.selected = keywordSelectionHistory[keyword.label];
      });

      topic.articles.forEach(function(article){
        article.selected = articleSelectionHistory[article.realId]
      });
    });
  }

  function setArticleSelection(id, selection){
    $scope.topics.forEach(function(topic){
      topic.articles.forEach(function(article){
        if(article.realId == id) article.selected = selection;

        article.authors.forEach(function(author){
          author.articles.forEach(function(item){
            if(author.numArticles < 6){
              if(item.realId == id) item.selected = selection;
            }else{
              item.articles.forEach(function(article){
                if(article.realId == id) article.selected = selection;
              });
            }
          });

          if(author.otherArticles){
            author.otherArticles.forEach(function(article){
              if(article.realId == id) article.selected = selection;
            });
          }
        });
      });
    });
  }

  function setKeywordSelection(label, selection){
    $scope.topics.forEach(function(topic){
      topic.keywords.forEach(function(keyword){
        if(keyword.label == label) keyword.selected = selection;
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
    if(author.numArticles < 6){
      author.articles.forEach(function(article){
        article.selected = articleSelectionHistory[article.realId]
      });
    }else{
      author.articles.forEach(function(topic){
        topic.articles.forEach(function(article){
          article.selected = articleSelectionHistory[article.realId]
        });
      });
    }

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

    if(selectedArticlesCount > 0) return false;

    var selectedKeywordsCount = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.keywords);
      }, [])
      .where({ selected: true })
      .value()
      .length;

    if(selectedKeywordsCount > 0) return false;

    var selectedAuthorArticlesCount = 0;

    var authors = _.chain($scope.topics)
      .reduce(function(all, topic){
        return all.concat(topic.articles);
      }, [])
      .uniq(function(article){ return article.realId })
      .reduce(function(all, article){
        return all.concat(article.authors)
      }, [])
      .uniq(function(author){ return author.id })
      .value();

    var selectedAuthorArticleFound = false;

    authors.forEach(function(author){
      author.articles.forEach(function(item){
        if(author.numArticles < 6){
          if(item.selected){
            selectedAuthorArticleFound = true;
          }
        }else{
          item.articles.forEach(function(article){
            if(article.selected){
              selectedAuthorArticleFound = true;
            }
          });
        }
      });

      if(author.otherArticles){
        if(_.where(author.otherArticles, { selected: true }).length > 0) selectedAuthorArticleFound = true;
      }
    });

    return !selectedAuthorArticleFound;
  }

  $scope.nextIteration = function(){
    window.scrollTo(0, 0);

    $scope.showAuthor = false;
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

      $scope.topics.forEach(function(topic){
        topic.articlesDisplaying = 2;
        topic.keywordsDisplaying = $scope.settings.keywordCount;
      });

      $scope.isLoading = false;
    });
  }

  $scope.showMoreArticles = function(topic){
    topic.articlesDisplaying += 5;
  }

  $scope.showMoreKeywords = function(topic){
    topic.keywordsDisplaying += 10;
  }

  $scope.toggleKeyword = function(keyword){
    keyword.selected = !keyword.selected;

    keywordSelectionHistory[keyword.label] = keyword.selected;

    setKeywordSelection(keyword.label, keyword.selected);

    if(keyword.selected){
      iterationSelections.push(keyword);
    }else{
      delete keywordSelectionHistory[keyword.label]
      _.remove(iterationSelections, function(selection){ return selection.id == keyword.id });
    }
  }

  $scope.moreArticlesFromAuthor = function(){
    API.moreArticlesFromAuthor({ index: $scope.chosenAuthor.index })
      .then(function(articles){
        articles.data.forEach(function(article){
          article.selected = articleSelectionHistory[article.realId];
        });

        $scope.chosenAuthor.otherArticles = $scope.chosenAuthor.otherArticles || [];
        $scope.chosenAuthor.otherArticles = $scope.chosenAuthor.otherArticles.concat(articles.data);
        $scope.chosenAuthor.moreArticlesDisplaying = true;

        if(articles.data.length == 0){
          $scope.chosenAuthor.noMoreArticles = true;
        }
      });
  }

  $scope.toggleArticle = function(article){
    article.selected = !article.selected;

    articleSelectionHistory[article.realId] = article.selected;

    setArticleSelection(article.realId, article.selected);

    if(article.selected){
      iterationSelections.push(article);
    }else{
      _.remove(iterationSelections, function(selection){ return selection.id == article.id });
    }
  }
});

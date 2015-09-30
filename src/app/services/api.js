SearchApp.service('API', function($http){
  this.search = function(options){
    return $http.get('api/search', {
      params: { keywords: options.keywords, topic_count: options.topicCount, keyword_count: options.keywordCount }
    });
  }

  this.next = function(options){
    return $http.post('api/next', options.selections);
  }

  this.moreArticlesFromAuthor = function(options){
    return $http.get('api/more_articles_from_author/' + options.index);
  }
});

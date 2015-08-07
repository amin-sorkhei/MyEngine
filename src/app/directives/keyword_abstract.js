SearchApp.directive('keywordAbstract', function() {
  return {
    scope: {
      abstract: '=',
      keywords: '=',
      keywordOnClick: '=',
      topicName: '='
    },
    link: function(scope, elem, attrs){
      var highlight = function(abstract, keywords){
        var abstractWords = abstract.split(' ');

        abstractWords.forEach(function(word, index){
          keywords.forEach(function(keyword){
            var keywordIndex = word.toLowerCase().indexOf(keyword.label.toLowerCase());

            if(keywordIndex >= 0){
              var wordStart = word.substring(0, keywordIndex);
              var wordEnd = word.substring(keywordIndex + keyword.label.length, word.length);
              var selectedClass = keyword.selected ? ' active' : '';
              var highlighted = wordStart + '<span class="highlight' + selectedClass + '">' + keyword.label + '</span>' + wordEnd;

              abstractWords[index] = highlighted;
              return;
            }
          });
        });

        return abstractWords.join(' ')
      }

      scope.$watch('abstract', function(texExpression) {
        elem.html(highlight(texExpression, scope.keywords));

        $(elem).find('.highlight').on('click', function(){
          var $targetKeyword = $(this);

          scope.$apply(function(){
            keyword = scope.keywordOnClick($targetKeyword.text(), scope.topicName);

            if(keyword.selected){
              $targetKeyword.addClass('active')
            }else{
              $targetKeyword.removeClass('active');
            }
          });
        });

        MathJax.Hub.Queue(['Typeset', MathJax.Hub, elem[0]]);
      });

      scope.$watch('keywords', function(keywords){
        var selected = _.where(keywords, { selected: true });

        $(elem).find('.highlight').each(function(){
          var keywordText = $(this).text();

          var matchingKeywords = _.find(selected, { label: keywordText });

          if(matchingKeywords){
            $(this).addClass('active');
          }else{
            $(this).removeClass('active');
          }
        });
      }, true);
    }
  }
});

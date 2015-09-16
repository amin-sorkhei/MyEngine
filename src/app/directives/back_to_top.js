SearchApp.directive('backToTop', function(){
  return {
    template: '<i class="fa fa-chevron-up"></i> Back to top',
    link: function(scope, elem, attrs){
      $(elem).on('click', function(){
        window.scrollTo(0,0);
      });

      $(elem).addClass('back-to-top-btn');

      $(window).on('scroll', function(){
        var topScroll = $(window).scrollTop();

        if(topScroll > 400){
          $(elem).addClass('bring-up');
        }else{
          $(elem).removeClass('bring-up');
        }
      });
    }
  }
});

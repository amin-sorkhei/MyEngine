var gulp = require('gulp');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');
var less = require('gulp-less');
var concat = require('gulp-concat');

gulp.task('script', function() {
  gulp.src(['./src/app/app.js', './src/app/services/*.js', './src/app/controllers/*.js', './src/app/directives/*.js'])
  .pipe(concat('app.min.js'))
  .pipe(gulp.dest('./dist'));
});

gulp.task('less', function(){
  return gulp.src('./src/less/*.less')
  .pipe(less())
  .pipe(concat('app.min.css'))
  .pipe(gulp.dest('./dist'));
});

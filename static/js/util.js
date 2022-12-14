// extends jQuery.form:

$(function () {
  console.log('Extends $form...');
  $.fn.extend({
      showFormError: function (err) {
          return this.each(function () {
              var
                  $form = $(this),
                  $alert = $form && $form.find('.uk-alert-danger'),
                  fieldName = err && err.data;
              if (! $form.is('form')) {
                  console.error('Cannot call showFormError() on non-form object.');
                  return;
              }
              $form.find('input').removeClass('uk-form-danger');
              $form.find('select').removeClass('uk-form-danger');
              $form.find('textarea').removeClass('uk-form-danger');
              if ($alert.length === 0) {
                  console.warn('Cannot find .uk-alert-danger element.');
                  return;
              }
              if (err) {
                  $alert.text(err.message ? err.message : (err.error ? err.error : err)).removeClass('uk-hidden').show();
                  if (($alert.offset().top - 60) < $(window).scrollTop()) {
                      $('html,body').animate({ scrollTop: $alert.offset().top - 60 });
                  }
                  if (fieldName) {
                      $form.find('[name=' + fieldName + ']').addClass('uk-form-danger');
                  }
              }
              else {
                  $alert.addClass('uk-hidden').hide();
                  $form.find('.uk-form-danger').removeClass('uk-form-danger');
              }
          });
      },
      showFormLoading: function (isLoading) {
          return this.each(function () {
              var
                  $form = $(this),
                  $submit = $form && $form.find('button[type=submit]'),
                  $buttons = $form && $form.find('button');
                  $i = $submit && $submit.find('i'),
                  iconClass = $i && $i.attr('class');
              if (! $form.is('form')) {
                  console.error('Cannot call showFormLoading() on non-form object.');
                  return;
              }
              if (!iconClass || iconClass.indexOf('uk-icon') < 0) {
                  console.warn('Icon <i class="uk-icon-*>" not found.');
                  return;
              }
              if (isLoading) {
                  $buttons.attr('disabled', 'disabled');
                  $i && $i.addClass('uk-icon-spinner').addClass('uk-icon-spin');
              }
              else {
                  $buttons.removeAttr('disabled');
                  $i && $i.removeClass('uk-icon-spinner').removeClass('uk-icon-spin');
              }
          });
      },
      postJSON: function (url, data, callback) {
          if (arguments.length===2) {
              callback = data;
              data = {};
          }
          return this.each(function () {
              var $form = $(this);
              $form.showFormError();
              $form.showFormLoading(true);
              _httpJSON('POST', url, data, function (err, r) {
                  if (err) {
                      $form.showFormError(err);
                      $form.showFormLoading(false);
                  }
                  callback && callback(err, r);
              });
          });
      }
  });
});

// ajax submit form:

function _httpJSON(method, url, data, callback) {
  var opt = {
      type: method,
      dataType: 'json'
  };
  if (method==='GET') {
      opt.url = url + '?' + data;
  }
  if (method==='POST') {
      opt.url = url;
      opt.data = JSON.stringify(data || {});
      opt.contentType = 'application/json';
  }
  $.ajax(opt).done(function (r) {
      if (r && r.error) {
          return callback(r);
      }
      return callback(null, r);
  }).fail(function (jqXHR, textStatus) {
      return callback({'error': 'http_bad_response', 'data': '' + jqXHR.status, 'message': '???????????????????????? (HTTP ' + jqXHR.status + ')'});
  });
}

function getJSON(url, data, callback) {
  if (arguments.length===2) {
      callback = data;
      data = {};
  }
  if (typeof (data)==='object') {
      var arr = [];
      $.each(data, function (k, v) {
          arr.push(k + '=' + encodeURIComponent(v));
      });
      data = arr.join('&');
  }
  _httpJSON('GET', url, data, callback);
}

function postJSON(url, data, callback) {
  if (arguments.length===2) {
      callback = data;
      data = {};
  }
  _httpJSON('POST', url, data, callback);
}
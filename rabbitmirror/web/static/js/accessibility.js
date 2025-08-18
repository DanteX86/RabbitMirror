// Accessibility enhancements for RabbitMirror UI
// - If form_error is present, move focus to the upload file input for immediate correction
(function(){
  try {
    function focusUploadIfInvalid(){
      var err = document.getElementById('upload-error');
      var input = document.getElementById('historyFile');
      if (err && input) {
        // Only focus if not already focused to avoid disrupting keyboard users
        if (document.activeElement !== input) {
          input.focus({ preventScroll: true });
        }
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', focusUploadIfInvalid);
    } else {
      focusUploadIfInvalid();
    }
  } catch (e) {
    // no-op
  }
})();

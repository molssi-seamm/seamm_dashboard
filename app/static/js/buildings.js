$(document).ready(function() {

  $('#buildings').DataTable({
    "language": {
      "searchPlaceholder": "Enter search terms"
    }
  });
  $('#buildings').attr('style', 'border-collapse: collapse !important');
  setBreadcrumb(['Home', 'Admin', 'Buildings']);

  $('.btn-del-confirm').on('click', function() {
    $.confirm({
      title: 'Confirmation',
      type: 'red',
      escapeKey: true,
      content: 'To delete this <strong>XYZ</strong> building, you have to <strong>manually</strong> delete all the rooms associated with it? <div>Are you sure you want to delete <strong>XYZ</strong> building?</div>',
      theme: 'bootstrap',
      container: '#ui-view',
      closeIcon: true,
      backgroundDismiss: true,
      buttons: {
        Ok: {
          btnClass: 'btn-success',
          keys: [
            'enter'
          ],
          action: function() {
            $(".breadcrumb").notify(
              "Building was deleted successfully", {
                clickToHide: true,
                autoHide: true,
                autoHideDelay: 5000,
                arrowShow: false,
                position: 'bottom center',
                style: 'bootstrap',
                className: 'success',
                showAnimation: 'slideDown',
                showDuration: 400,
                hideAnimation: 'slideUp',
                hideDuration: 200,
                gap: 10
              });
          }
        },
        Cancel: {
          btnClass: 'btn-danger',
          keys: [
            'ctrl',
            'shift'
          ]
        }
      },
      columnClass: 'col-md-6 col-md-offset-3'
    });
  });

});
$('select[name="wallet_name"]').on('change', function() {
      var sel = $(this).val();
          if (sel == "BTC") {
           $('.input-group-addon').text("BTC");}
          else if (sel == "ETH") {
            $('.input-group-addon').text("ETH");
          }else if(sel == "LTC") {
           $('.input-group-addon').text("LTC");
          }
       });

       
$("#amount_main").on("change paste keyup", function () {
  var form = $(this).closest("form");
  $.ajax({
    type: 'POST',
    url: form.attr("data-validate-username-url"),
    data: form.serialize(),
    dataType: 'json',
    success: function (data) {
         $('#amount_choosen').val(data.amount);
    }
  });

});

$("#sell_main").on("change paste", function () {
  var form = $(this).closest("form");
  $.ajax({
    type: 'POST',
    url: $('#sell_main').attr("data-validate-username-url"),
    data: form.serialize(),
    dataType: 'json',
    success: function (data) {
        $("label[for='sellInputError']").html(data.error);
        $("#sell_btn").attr("class", data.alw);
    }
  });

});


$('select[name="wallet_list"]').on('change', function() {
  var sel = $(this).val();
  $('#btnwll').val(sel);
  $('#myT').html('').load('get_addresses_for_account', { sel: sel, csrfmiddlewaretoken: '{{ csrf_token }}' });
});

$(".getTxs").click(function() {
    var sel = $(this).prop('name');
    $('#txs_table').html('').load('get_transactions_for_account', { sel: sel, csrfmiddlewaretoken: '{{ csrf_token }}' });
});
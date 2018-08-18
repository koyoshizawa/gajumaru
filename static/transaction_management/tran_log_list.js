
//グラフ描写用データ作成
function createLineChartData(data){
    // データリスト作成
    let hLabel = [];  // 横軸ラベルリスト
    let dataList = [];  // 時系列データリスト
    let statusList = [];  // 状態リスト
    let hasTradeList = [];  // 取引有無リスト
    let profitLossList = [];  // 損益リスト

    console.log(data)
    for (var i = 0; i<data.length; i++){
        hLabel.push(data[i].date_time);
        dataList.push(data[i].rate);
        statusList.push(data[i].status);
        hasTradeList.push(data[i].has_trade);
        profitLossList.push(data[i].profit_loss);
    }
    console.log(dataList, statusList, hasTradeList, profitLossList)

    // 状態によってマーカーの色を変化させる
    let markerColorList = []
    color_map = {'a': 'rgba(135, 206, 235, 1.0)',
                 'b': 'rgba(235, 134, 206, 1.0)',
                 'c': 'rgba(235, 162, 134, 1.0)',
                 'd': 'rgba(134, 235, 162, 1.0)'}

    for (var i = 0; i<statusList.length; i++) {

        switch(statusList[i]) {
            case 'a':
                markerColorList.push(color_map.a);
                break;
            case 'b':
                markerColorList.push(color_map.b);
                break;
            case 'c':
                markerColorList.push(color_map.c);
                break;
            case 'd':
                markerColorList.push(color_map.d);
                break;
        }
    }

    // 取引の有無でマーカーの大きさを変化させる
    let markerRadiusList = [];
    for (var i = 0; i<hasTradeList.length; i++) {
        if(hasTradeList[i]){
            markerRadiusList.push(10)
        } else {
            markerRadiusList.push(4)
        }
    }

    // 取引の勝ち負けでマーカーの枠線の色を変化させる
    let markerBorderColorList = [];
    let markerBorderWidthList = [];
    for (var i = 0; i<profitLossList.length; i++) {
        if(profitLossList[i]>0){
            markerBorderColorList.push('rgba(0, 0, 205, 1.0)');
            markerBorderWidthList.push(2)
        } else if (profitLossList[i]<0) {
            markerBorderColorList.push('rgba(255, 0, 0, 1.0)');
            markerBorderWidthList.push(2)
        } else {
            markerBorderColorList.push('rgba(0, 0, 0, 0)');
            markerBorderWidthList.push(1)

        }
    }

    let lineChartData = {
        // 横軸ラベル
        labels: hLabel,
        datasets: [{
//            label: '日経先物MINI',
            data: dataList,
            backgroundColor: "rgba(255,153,0,0.4)",
            pointBackgroundColor: markerColorList,
            pointBorderColor: markerBorderColorList,
            pointBorderWidth: markerBorderWidthList,
            pointRadius: markerRadiusList,
            fill: false,
        }]
    }

    return lineChartData
}


$(function(){
    // updateボタン押下をキーにフィルターされた情報を表示する
    $('#update_btn').on('click', function(){
        // フィルター条件抽出
        let startDate = $('#start_date').val()
        let endDate = $('#end_date').val()
        let productName = $('#product_name').val()

        let data = {
            start_date: startDate,
            end_date: endDate,
            product_name: productName,
        }

        // フィルター条件をサーバーに送信
        let url = 'http://localhost:8000/transaction_management/tran_log_list'
        $.ajax({
            url: url,
            type:'GET',
            dataType: 'json',
            data : data,
        }).done(function(data) {
            // テーブルにある行を全て削除
            $('#data_table').find("tr:gt(0)").remove()

            // テーブルにデータを表示
            for (var i=0; i<data.data_set.length; i++){
                let html = '<tr><td>' + data.data_set[i].product_name + '</td><td>' + data.data_set[i].date_time + '</td><td>' +　data.data_set[i].rate + '</td><td>' + data.data_set[i].status + '</td><td>' + data.data_set[i].position + '</td><td>' + data.data_set[i].profit_loss + '</td><td>' +  data.data_set[i].has_trade + '</td></tr>'
                $('#data_table').append(html)
            }
            // チャート描写
            let ctx = $('#canvas');
            let myChart = new Chart(ctx, {
                type: 'line',
                data: createLineChartData(data.data_set),
                options: {

                }
            })


        }).fail(function(XMLHttpRequest, textStatus, errorThrown) {
                         alert("error");
        })

    })



//    let legendStr = "<div>" +
//    "<ul style='color: rgba(135, 206, 235, 1.0)'><li style='color:#333;'><span>A</span></li></ul>" +
//    "<ul style='color: rgba(235, 134, 206, 1.0)'><li style='color:#333;'><span>B</span></li></ul>" +
//    "<ul style='color: rgba(235, 162, 134, 1.0)'><li style='color:#333;'><span>C</span></li></ul>" +
//    "<ul style='color: rgba(134, 235, 162, 1.0)'><li style='color:#333;'><span>D</span></li></ul>" +
//    "</div>";


})
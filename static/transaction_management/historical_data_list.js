

//グラフ描写用データ作成
function createLineChartData(data){

    // データリスト作成
    let hLabel = []  // 横軸ラベルリスト
    let dataList = []  // 時系列データリスト

    // データ整形
    for (var i=0; i<data.length; i++){
        hLabel.push(data[i].date_time)
        dataList.push(data[i].rate)
    }

    // chart.js に渡すようにデータの形を調整
    let lineChartData = {
        labels: hLabel,
        datasets: [{
            data: dataList
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
        let url = 'http://localhost:8000/transaction_management/historical_data_list'
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
                let html = '<tr><td>' + data.data_set[i].product_name + '</td><td>' + data.data_set[i].date_time + '</td><td>' +　data.data_set[i].rate + '</td></tr>'
                $('#data_table').append(html)
            }

            // チャート描写
            let ctx = $('#canvas')
            let myChart = new Chart(ctx, {
                type: 'line',
                data: createLineChartData(data.data_set),
                options: {
                    title: {
                        display: true,
                        text: data.data_set[0].product_name,
                        fontSize: 16,
                    }

                }
            })
        }).fail(function(XMLHttpRequest, textStatus, errorThrown) {
                         alert("error");
        })
    })



})
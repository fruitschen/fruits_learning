var global_interval;
var download_interval;
if(typeof(global_interval) != undefined){
    clearInterval(global_interval);
    clearInterval(download_interval);
}
var $ = window.jQuery;
window.stocks = {}
window.pairs = [

]

window.update_stocks = function(){
    $('.optional_stocks tbody tr').each(function(n){
        td_nodes = $(this).find('td');
        name = $('a.name', td_nodes[0]).text()
        code = $('a.code', td_nodes[0]).text()
        price = $('span', td_nodes[1]).text()
        stocks[code] = {
            'code': code,
            'name': name,
            'price': price,
        }

    })
}

window.update_pairs = function(){
    for (i in pairs){
        pair = pairs[i];
        stock1 = pair.pair[0];
        stock2 = pair.pair[1];
        price1 = stocks[stock1]['price'];
        price2 = stocks[stock2]['price'];
        pair['ratio'] = parseFloat(price1)/parseFloat(price2)
        pair['name'] = stocks[stock1]['name'] + '/' + stocks[stock2]['name'];
    }
}

window.update_display = function(){
    $('.user__col--lf').hide();
    $('.home__col--rt').width(450);
    first_panel = $('.home__business')[0];
    $(first_panel).html('').css('margin-top', '160px');
    n = new Date();
    $(first_panel).append('<li>' + n.toLocaleTimeString() + '</li>')
    for (i in pairs){
        pair = pairs[i];
        content = '<strong>' + pair['name'] + '</strong> <br> <strong>' + pair['ratio'].toFixed(3) + '</strong>'
        if(pair.note){
            content = content + '<span> ' + pair.note + '</span>'
        }
        $(first_panel).append('<li style="padding:10px;">' + content + '</li>')
    }
}

// Function to download data to a file
window.download = function (data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.target='_blank';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 0);
    }
}

window.update_all = function(){
    update_stocks();
    update_pairs();
    update_display();
}

window.download_stocks = function(){
    n = new Date();
    if (n.getHours() > 9 && n.getHours() < 15){
        download(JSON.stringify(stocks), 'stocks_updates.json', 'text/plain');
    }
}

function init(){
    global_interval = window.setInterval(update_all, 3000);
    download_interval = window.setInterval(download_stocks, 60 * 1000);
}

init();
update_all();

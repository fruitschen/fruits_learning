var global_interval;
var download_interval;
if(typeof(global_interval) != undefined){
    clearInterval(global_interval);
    clearInterval(download_interval);
}
var $ = window.jQuery;
window.stocks = {}
window.pairs = [
    {% for pair in pairs %}{
        'pair': ['{{ pair.started_stock.market.upper }}{{ pair.started_stock.code }}', '{{ pair.target_stock.market.upper }}{{ pair.target_stock.code }}'],
        'note': {{ pair.note }},
        'transactions': [
        {% if pair.unfinished_transactions %}
            {% for t in pair.unfinished_transactions %}
                {'ratio': {{ t.to_ratio }}, 'same_direction': {{ t.same_direction|lower }},
                'text': '{{ t.bought_stock.name }} x {{ t.bought_amount }}. -> {{ t.sold_stock.name }} x {{ t.sold_amount }}', }{% if not forloop.last %},{% endif %}
            {% endfor %}
        {% else %}
            {% for t in pair.recent_finished_transactions %}
                {'ratio': {{ t.to_ratio }}, 'same_direction': {{ t.same_direction|lower }},
                'text': '已完成. {{ t.finished|date:"Y-m-d" }}', }{% if not forloop.last %},{% endif %}
            {% endfor %}
        {% endif %}
        ]
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
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
        if(pair.transactions){
            for (j in pair.transactions){
                transaction = pair.transactions[j];
                trans_ratio = transaction.ratio;
                fee = 0.002; // assume total fee is 0.2%
                if(transaction.same_direction){
                    change = (1- pair['ratio'] / trans_ratio - fee) * 100
                }else{
                    change = (pair['ratio'] / trans_ratio - 1 - fee) * 100
                }
                if(change > 0){
                    sign = '+'
                    color = 'red'
                }else{
                    sign = ''
                    color = 'green'
                }
                change_text = '<strong style="color: ' + color + '">(' + sign + change.toFixed(2) + '%)</strong>'
                content = content + '<br /><span> ' + trans_ratio.toFixed(3) + change_text + ' | ' + transaction.text + '</span>'
            }
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
    open_cond_1 = n.getHours() == 9 && n.getMinutes() > 25
    open_cond_2 = n.getHours() > 9
    end_cond_1 = n.getHours() == 11 && n.getMinutes() < 30
    end_cond_2 = n.getHours() < 11
    open_morning = (open_cond_1 || open_cond_2) && (end_cond_1 || end_cond_2)

    open_cond_pm = n.getHours() >= 13
    end_cond_pm = n.getHours() < 15
    open_afternoon = open_cond_pm && end_cond_pm

    open = open_morning || open_afternoon

    if (open){
        download(JSON.stringify(stocks), 'stocks_updates.json', 'text/plain');
    }
}

function init(){
    global_interval = window.setInterval(update_all, 3000);
    download_interval = window.setInterval(download_stocks, 60 * 1000);
}

init();
update_all();

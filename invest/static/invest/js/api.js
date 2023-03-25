const baseApiURL = 'http://127.0.0.1:8000/api/'

function makeRequest(method, url, data=undefined, callback=undefined) {
    let xhr = new XMLHttpRequest()
    if (!xhr) {
        alert('Cannot create an XMLHTTP instance')
        return false
    }
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                let response = JSON.parse(xhr.responseText)
                if (callback) callback(response)
            } else {
                alert('There was a problem with the request.')
            }
        }
    }
    if (method == 'GET') {
        xhr.open('GET', url)
        xhr.send()
    } else if (method == 'POST') {
        xhr.open('POST', url)
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
        xhr.send(JSON.stringify(data))
    }
}

queryStrDeserializer = function(obj) {
    // Build query string from an object.
    var str = [];
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        }
    }
    return str.join("&");
}

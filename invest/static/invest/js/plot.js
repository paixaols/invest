function plot(x, datasets, ctx, labels={}) {
    let displayLegend = datasets[0].hasOwnProperty('label') ? true : false

    let xLabel = labels.hasOwnProperty('xlabel') ? labels.xlabel : ''
    let yLabel = labels.hasOwnProperty('ylabel') ? labels.ylabel : ''
    let title = labels.hasOwnProperty('title') ? labels.title : ''

    datasets.forEach(element => {
        element.borderWidth = 1
    })

    const config = {
        type: 'bar',
        data: {
            labels: x,
            datasets: datasets
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: (xLabel === '') ? false : true,
                        text: xLabel
                    }
                },
                y: {
                    title: {
                        display: (yLabel === '') ? false : true,
                        text: yLabel
                    }
                }
            },
            plugins: {
                legend: {display: displayLegend},
                title: {
                    display: (title === '') ? false : true,
                    text: title
                }
            }
        }
    }
    new Chart(ctx, config)
}

function djangoQuerysetDeserializer(json, xField, yField) {
    const contextObj = JSON.parse(json)
    let x = []
    let y = []
    for (i in contextObj) {
        let fieldsObj = contextObj[i].fields
        x.push(fieldsObj[xField])
        y.push(fieldsObj[yField])
    }
    return [x, y]
}

function delay(t, v) {
    return new Promise(function(resolve) { 
        setTimeout(resolve.bind(null, v), t)
    });
}

function randomValue(value, min, max) {
    if(!min) min = Math.ceil(value - 500)
    if(!max) max = Math.floor(value + 500)
    return Math.floor(Math.random() * (max - min) + min); //The maximum is exclusive and the minimum is inclusive
}

module.exports = { delay, randomValue }
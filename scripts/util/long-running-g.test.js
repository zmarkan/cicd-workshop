const assert = require('assert')
const { delay, randomValue } = require('./test-utils')

describe("Long running test file G", function()  {
    this.timeout(0)
    it("Should wait for 3 seconds 1", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })
    it("Should wait for 3 seconds 2", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })

    it("Should wait for 3 seconds 3", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })
    it("Should wait for 3 seconds 4", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })
    it("Should wait for 3 seconds 5", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })
    it("Should wait for 3 seconds 6", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })
    it("Should wait for 3 seconds 7", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })
    it("Should wait for 3 seconds 8", async () => {

        await delay(randomValue(3000))

        assert.ok(true)
    })


})





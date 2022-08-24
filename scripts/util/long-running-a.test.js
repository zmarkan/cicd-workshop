const assert = require('assert')
const { delay, randomValue } = require('./test-utils')

describe("Long running test file A", () => {

    it("Should wait for a second 1", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })

    it("Should wait for a second 2", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })

    it("Should wait for a second 3", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
    it("Should wait for a second 4 ", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
    it("Should wait for a second 5 ", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
    it("Should wait for a second 6 ", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
    it("Should wait for a second 9", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
    it("Should wait for a second 7 ", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
    it("Should wait for a second 8", async () => {

        await delay(randomValue(1000))

        assert.ok(true)
    })
})





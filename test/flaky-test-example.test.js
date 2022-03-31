var request = require("request"),
    assert = require('assert'),
    // helloWorld = require("../app.js"),
    base_url = "http://localhost:5000/";

describe("Flaky sample!", function() {

  // describe("Failing test", function (){
  //   it("shall not pass", function(){
  //     assert.strictEqual(true, false);
  //   });  
  // });

  describe("A flakey test", () => {

    it("works every time, 60% of the time", () => {
      let dice = Math.random()
      let testedValue = dice >= 0.4 ? true : false
  
      assert.ok(testedValue, `Dice roll  less than 0.4 ${dice}`)
    })
  })


});

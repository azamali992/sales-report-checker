const assert=require('node:assert/strict');
const fs=require('node:fs');
const engine=require('../assets/engine.js');
assert.equal(engine.amountPence(3,'0.005'),2);
assert.equal(engine.amountPence(-3,'0.005'),-2);
assert.equal(engine.amountPence(1,'0.001'),0);
assert.equal(engine.amountPence(-1,'-11062.06'),1106206);
assert.throws(()=>engine.amountPence(1.5,'2.55'));
assert.throws(()=>engine.amountPence(1,'NaN'));
assert.throws(()=>engine.amountPence(1,'1e6'));
assert.throws(()=>engine.amountPence(1,'900719925474099100'));
const sample=JSON.parse(fs.readFileSync('data/sample.json','utf8')).rows;
const results=JSON.parse(fs.readFileSync('eval/results.json','utf8'));
for(const [key,expected] of Object.entries(results.sample_policies)){
    const policy={mode:expected.policy,excludeDescription:expected.exclude_description,excludeCustomer:expected.exclude_customer};
    const actual=engine.summarize(sample,policy);
    assert.equal(actual.rawPence,expected.raw_pence,key);
    assert.equal(actual.includedPence,expected.included_pence,key);
    assert.equal(actual.excludedPence,expected.excluded_pence,key);
    assert.equal(actual.includedRows,expected.included_rows,key);
    assert.equal(actual.identityVerified,true);
    assert.equal(Object.values(actual.groups).reduce((n,g)=>n+g.rows,0),sample.length);
}
console.log('JS decimal rounding/bounds and all 5 real-sample policy checks passed.');

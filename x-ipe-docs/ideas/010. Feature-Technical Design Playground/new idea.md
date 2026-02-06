For technical design skill, for now it will base on feature specification to create technical-design.md, it's good, but more, during technical design phase, I would like to have more transparency of what would be implemented at architecture/skeleton level which it need to let me know what major class and functions would be created and how would they work with each other.

So I got ideas as below:

## For technical design skill
- beside technical-design.md, it need to create an extra file called "technical-design-playground.tdpg"
- technical design need to base on it's understand to create key class and functions and then use  technical-design dsl to generate "technical-design-playground.tdpg"

### For technical-design-playground.md
- it contains only technical-design dsl
- the dsl syntax you can learn from /instance/trace, for the input and output, since here is for class and function definition, so no detailed value should provided(example is suggested)


## Viewing tdpg file in X-IPE
- when we view tdpg in X-IPE, just like detailed tracing view in application tracing, we need show the topology of classes and functions. 
- we also want to have a feedback function similar to feedback function in UIUX Feedbacks. I should able to select multipule class or function node to provide feedbacks. then save these feedbacks in x-ipe/technical-design-feedbacks. the feedback file format you can also learn from x-ipe/uiux-feedback

Please help refine my idea

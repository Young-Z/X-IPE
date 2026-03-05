1. since for implementation we may have different type of 'code' need to be implemented, for example for 'frontend code', for 'backend
  code', for 'java code', for 'python code'... so for  Separation of Concerns,  Abstraction, Loose Coupling. why not for
  x-ipe-task-based-implementation-skill skill, provides a basic skeleton and more focus on task based flow, for diferent language and
  purpose, let's having different tool level implementation to cover the detail, and then have task-based-implementation skill to invoke them base on the needs.
	
	2. since tests are related to the implementation language, lib or purpose. so why not we elimate x-ipe-tools-generate test skill. and for no matter which implementation tool skill introduced. it should should having both test and coding as following steps:
	> step 1: study feature and tecnical design to list all the testing cases for happy and said path
	> step 2: implement the code follow the requirement from feature and technical design.
	> step 3: base on the code to implemente the test case and test the code.
	
	3. since for one feature, it may need many implement tool skill to working together to implement the feature, for example that html5 tool skill and python tool skills may need work together to buildup a web application. so for implementation task based skill it need make sure all these tool based skill can work seamlessly together for implementing the feature and meet technical design requirements.
	
	4. we should have a general purpose implementation for any kind of code implementation as a fallback. so if no any specific implementation tools matched, use general purpose implemention tool skill in task based implementation skill.
	
	5. common implemention tool skills I can come up are
	 > 1. html 5 implementation skills including html, js, css and support any common frameworks and libraries.
	 > 2. python implementation skills supports any common framework and libraries for any type of python codes.
	 > 3. typescripts and java skills accordingly.
	 
	6. for each implementation tool skills, you can search online for it's best practice and principles for implemente coding and testing.
	
	7. implementation task based skill should define the entry of the source code, for most cases, implement tool skills need to base on the source code path defined in it.
	
	8. last base on your understanding of the x-ipe to propose anything I may missed and refine the idea
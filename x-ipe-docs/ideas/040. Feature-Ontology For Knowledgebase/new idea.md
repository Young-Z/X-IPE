The knowledge tagging in the existing ai librarian is not efficient, it's too basic, we may need multi dimension analysis to learn the knowledge and give more meaningful and dimentional tagging to the knowledge, so let's introduce ontology for knowledge base, the idea is below

1. adding a tool skill called 'x-ipe-tool-ontology', it as following capability
  > it has knowledge tagging operation, it should follow ‘格物’，‘致知’ two phases for it.
     a. '格物' - study the knowledge and understand it, if you don't understand it, you can call web search skill to search online.
		 b. '致知' - listing the tagging dimension base on your understanding of the knowledge and the tagging output format from input parameter to generate taggings
	> it has knowledge graph creatation/recreation operation
	   a. which is able to collecting the taggs under a specific folder and it's sub folders, then form an ontology knowledge graphes(can be multi knowledge graphes, it the knowledge is no relationship)
		 b. save the knowledge graphes into .ontology under knowledge base. the knowledge-graph file name should use it's root node name to name it. (you should use script in the skill to do it)
		 c. you, as a world top knowledge graph designer ,should define a JSON format knowledge representation for the ontology knowledge graph (also define in script, so I can reuse it programmatically)
	> you should able to search the knowledge through the knowledge graph. and return the related knowledge and it's index info(tagging, knowledge desc ...)

2. update ai librarian skill, it should call x-ipe-tool-ontology for knowledge for tagging, then after all the knowledge processed, it should call the skill for recreation
  > double check and design the necessary parameters need to pass to the x-ipe-tool-ontology skill, and design the parameter to the skill.
 
3. update knowledge base uiux, we should have a view to view all the ontology knowledge graph
  > left side show the ontology graph files, right side show the knowledge graph
  > above the knowledge graph, we should have a. a search scope selector(click to expend then multi select the graph files), b. a search bar for wildcard text search under selected knowledge graph files, c. a search with AI Agent button.
  > search with AI Agent button details, when click on the button, it should just like other AI Agent prompt behavior, which open the terminal window, then auto type the prompt to call 'x-ipe-tool-ontology with selected graphs' path' and should be get ready for user search request.
  > after user given search request, it should call the tool to get search result and show on the knowledge graph view.
4. the knowledge graph view should use modern knowledge graph library for it. 
since knowledge related capability grow bigger and bigger, so let's organize it more systematically. here is the organize structure I suggest for all the knowledge related skills:

x-ipe-knowledge-*                                                           # introduce knowledge as a new type or namespace to x-ipe-meta-skill-creator(reuse task based skill structure, but not it's content, and all skills under it's namespace using this structure template)
|- x-ipe-knowledge-constructor-*                                 # introduce x-ipe-knowledge-constructor-* skills which used to format knowledge for holistic understanding the knowledge
|    |- x-ipe-knowledge-constructor-user-manual        # migrate x-ipe-tool-knowledge-extraction-user-manual skill to it, update it's core logic, previously knowledge-extractor skills call extraction-user-manual, now knowledge-librarian-DAO would replace knowledge extractor for coordination, so we need to integrate with assistant-knowledge-librarian-'DAO'
|    |- x-ipe-knowledge-constructor-notes                    # migrate x-ipe-tool-knowledge-extraction-notes, do the same change as for user-manual skill
|    |- x-ipe-knowledge-constructor-app-reverse-engineering        # migrate x-ipe-tool-knowledge-extraction-application-reverse-engineering, do the same as for user-manual skill
|
|- x-ipe-knowledge-extractor-*                                     # introduce x-ipe-knowledge-extractor-* skills which used to extract knowledge from target source.
|    |- x-ipe-knowledge-extractor-web                           # replace x-ipe-task-based-application-knowledge-extractor, and know the extractor-web only do knowledge extraction base on knowledge-librarians needs. so we need to integrate with assistant-knowledge-librarian-'DAO'
|    |- x-ipe-knowledge-extractor-memory                    # since we have knowledge everywhere, we have it in web, we have local knowledge in normal file system, we have knowledge in knowlege base. now let's give knowledge base a more fancy name 'Memory', and to access the memory we have this skill
|
|- x-ipe-knowledge-mimic-*                                          # introduce x-ipe-knowledge-mimic-* skills which used for dynamic knowledge(procedure or knowledge in a time series), so we need tracking them to consolidate from beiginning to end, to make it more static and easier to have a holistic view.
|    |- x-ipe-knowledge-mimic-web-behavior-tracker # migrate behavior-tracker-for-web skill to this skill.
|
|- x-ipe-knowledge-keeper-*                                         # introduce x-ipe-knowledge-keeper-* skills which used to save knowledge to a temp or persistent space.
|    |- x-ipe-knowledge-keeper-memory                       # replace existing knowledge-librarian skill to manage knowledge base, change the words from knowledge base to memory.
|    |- x-ipe-knowledge-keeper-staging                        # introduce x-ipe-knowledge-keeper-staging for coversation scope short term knowledge storage.
|
|- x-ipe-knowledge-present-*                                       # introduce x-ipe-knowledge-present-* skills which used to output knowledge to a target endpoint (can be user, api, device...)
     |- x-ipe-knowledge-present-to-user
		 |- x-ipe-knowledge-present-to-knowledge-graph


x-ipe-assistant-*                                                              # introduce assistant as a new type or namespace x-ipe-meta-skill-creator, use the structure, template of 'dao' type, then remove 'dao'
|- x-ipe-assistant-user-representative-Engineer         # just migrate x-ipe-assistant-user-representative-Engineer to this. Engineer(工程师) is the representative name, we no longer call it 'DAO'(道)
|- x-ipe-assistant-knowledge-librarian-DAO                # world is a big knowledge library, DAO(道) is the librarian can leverage all the knowledge related skills to achieve it's works. (it's not replace of original knowledge-librarian skill)

so the workflow of the new knowledge design

user inputs 
->(general AI: if knolwedge related) 
-> x-ipe-assistant-knowledge-librarian-DAO
  > input info intialization: check what knowledge request it is.
  > 格物 - strategic planning
  > 格物-step1: what we have, what user ask for
  > 格物-step2: make a plan to base on input to fufill user needs.
  > 致知-tactical execution
  > 致知-step1: follow plan to call the skills to get the knowledge
  > 致知-step2: save the knowledge properly
  > 致知-step3: response the request in right format

for example:

user inputs: learn to use xyz in abc.com 
-> (general AI: knowledge fetching) 
-> DAO: 
 > input info intialization: knowledge_type: user-manual, knowledge_request: learn, knowledge_output_format: knowledge_graph
 > 格物-step1:  we have x-ipe-knowledge-constructor-user-manual to form user manual related knowledge, we can use x-ipe-knowledge-extractor-web to get knowledge from abc.com, if abc.com cannot directly give me the user manual related info, we can use x-ipe-knowledge-mimic-web-behavior-tracker to track user behavior to learn to use it. we can use x-ipe-knowledge-keeper-staging  for temporarily save the knowledge into a place, then we can use x-ipe-knowledge-present-to-knowledge-graph to output a format to match with user request.
 > 格物-step2: base on the capabilities I have on my hand, I can fufill the request with following steps:
     a. xxxx
		 b. xxxx
		 ...
 > 致知-step1: follow plan to call the skills to get the knowledge, let's do ...
 > 致知-step2:  follow plan to call the skills to save the knowledge properly
 > 致知-step3:  follow plan to call the skills to response the request in right format


BTW we need update the wording in UI and documents, we no longer call knowledge base, we call it memory






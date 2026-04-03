change the rendering logic for task board.md and features.md
since it we are having more and more tasks and features, we need more efficient way to manage the feature and task board for both human and AI.
let's do the changes below.
1. separete data and ui, with markdown it serve both as data and ui, but the down side it's both can not be optimal. so for data let's save as json, for ui let's have a normal page with some search, display and filtering and loading json for display the data.
2. for task json data should be updated by a new skill called 'x-ipe-tool-task-board-manager'
   > it need to define the json structure with scripts (you can learn skill script by reference architecture dsl)
   > it need to support CRUD the json via scripts
   > the json file naming convension should include datetime.
3. for features json data should be updated by a new skill called 'x-ipe-tool-feature-board-manager'
	> logic the same as task board
5. for ui, let's provide normal web page for feature and task display.
  > for task board, there is fiter listing 1 week tasks, 1 month, all(need pagination, default is 1 week tasks)
7. for other skills contribute feature and tasks, let's replace the old logic to use new skill for feature board and task update
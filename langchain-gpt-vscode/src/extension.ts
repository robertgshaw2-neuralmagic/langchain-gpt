// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import axios from 'axios';

function callChain(userQuery: string): any {
	

	return "There was an issue with the request"
}

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "langchain-gpt-vscode" is now active!');

	let disposable = vscode.commands.registerCommand('langchain-gpt-vscode.langchainGPT', async () => {
		const inputOptions: vscode.InputBoxOptions = {
			prompt: "Type a description of what you would like to do in LangChain:",
		  };
		
		const userQuery = await vscode.window.showInputBox(inputOptions);

		if (userQuery !== undefined) {			
			const callChain = async (q: string): Promise<string> => {
				const response = await axios.get("http://localhost:8000/predict", {
					params: {
						query: q
					}
				})
				return response.data.result
			}

			const answer = await vscode.window.withProgress({
				location: vscode.ProgressLocation.Notification,
				title: "Searching...",
				cancellable: true
			}, (progress, token) => {
				token.onCancellationRequested(() => {
					console.log("User canceled the long running operation");
				});
					
				return callChain(userQuery);
			});
			
			vscode.window.showInformationMessage(answer);
		}
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}

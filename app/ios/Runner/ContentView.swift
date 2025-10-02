import SwiftUI

struct ContentView: View {
    @State private var messages: [ChatMessage] = []
    @State private var userInput: String = ""

    var body: some View {
        VStack {
            ScrollViewReader { scrollView in
                ScrollView {
                    LazyVStack {
                        ForEach(messages) { msg in
                            ChatBubble(message: msg)
                                .id(msg.id)
                        }
                    }
                }
                .onChange(of: messages.count) { _ in
                    if let last = messages.last {
                        withAnimation {
                            scrollView.scrollTo(last.id, anchor: .bottom)
                        }
                    }
                }
            }

            HStack {
                TextField("Type a message (optional note)...", text: $userInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: 40)

                Button(action: runRecipe) {
                    Text("Run Recipe")
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
            }
            .padding()
        }
        .padding()
    }

    func runRecipe() {
        // رسالة المستخدم (اختياريًا يكتب ملاحظة)
        if !userInput.isEmpty {
            let userMsg = ChatMessage(
                text: userInput,
                isUser: true,
                timestamp: Date(),
                provider: "User"
            )
            messages.append(userMsg)
            userInput = ""
        }

        APIService.shared.runRecipe { logs in
            DispatchQueue.main.async {
                let botMsg = ChatMessage(
                    text: logs,
                    isUser: false,
                    timestamp: Date(),
                    provider: "Runner"
                )
                messages.append(botMsg)
            }
        }
    }
}

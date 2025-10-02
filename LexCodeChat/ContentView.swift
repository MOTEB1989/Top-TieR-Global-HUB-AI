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
                TextField("Type a message...", text: $userInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: 40)

                Button(action: sendMessage) {
                    Text("Send")
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
            }
            .padding()
        }
    }

    func sendMessage() {
        let userMsg = ChatMessage(text: userInput, isUser: true, timestamp: Date())
        messages.append(userMsg)
        let query = userInput
        userInput = ""

        APIService.shared.sendMessage(query) { reply in
            DispatchQueue.main.async {
                let botMsg = ChatMessage(text: reply, isUser: false, timestamp: Date())
                messages.append(botMsg)
            }
        }
    }
}

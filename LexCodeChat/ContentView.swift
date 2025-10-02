import SwiftUI

struct ContentView: View {
    @State private var userMessage: String = ""
    @State private var botReply: String = "🤖 Awaiting your message..."

    var body: some View {
        VStack {
            Text("LexCode Chat")
                .font(.title)
                .padding()

            ScrollView {
                VStack(alignment: .leading, spacing: 10) {
                    Text("User: \(userMessage)")
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity, alignment: .leading)

                    Text("Bot: \(botReply)")
                        .foregroundColor(.green)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .padding()
            }

            TextField("Type your message...", text: $userMessage)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()

            Button(action: {
                APIService.shared.sendMessage(userMessage) { reply in
                    DispatchQueue.main.async {
                        self.botReply = reply
                    }
                }
            }) {
                Text("Send")
                    .bold()
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .padding()
        }
        .padding()
    }
}

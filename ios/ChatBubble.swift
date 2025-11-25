import SwiftUI

struct ChatBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.isUser { Spacer() }

            VStack(alignment: .leading, spacing: 4) {
                Text(message.text)
                    .padding()
                    .background(message.isUser ? Color.blue : Color.gray.opacity(0.2))
                    .foregroundColor(message.isUser ? .white : .black)
                    .cornerRadius(16)

                HStack(spacing: 4) {
                    Text(message.timestamp, style: .time)
                        .font(.caption2)
                        .foregroundColor(.gray)

                    if !message.isUser, let provider = message.provider {
                        Text("[\(provider.capitalized)]")
                            .font(.caption2)
                            .foregroundColor(.purple)
                    }
                }
            }

            if !message.isUser { Spacer() }
        }
        .padding(message.isUser ? .leading : .trailing, 50)
        .padding(.vertical, 4)
    }
}

struct ChatBubble_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 12) {
            ChatBubble(message: ChatMessage(text: "Hello!", isUser: true, timestamp: Date(), provider: nil))
            ChatBubble(message: ChatMessage(text: "Hi there", isUser: false, timestamp: Date(), provider: "openai"))
        }
        .padding()
    }
}

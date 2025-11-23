import express from 'express';
import dotenv from 'dotenv';
import { QdrantClient } from '@qdrant/js-client-rest';
import OpenAI from 'openai';

dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.API_PORT || 3001;
const QDRANT_URL = process.env.QDRANT_URL || 'http://localhost:6333';

// Initialize Qdrant client for vector database
const qdrant = new QdrantClient({ url: QDRANT_URL });

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Generate response using OpenAI API
async function generateResponse(query, context) {
  try {
    // Construct the system prompt with context and user query
    const systemPrompt = `You are a helpful assistant. Answer the user's query based on the provided context.

Context: ${context}`;

    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: query }
      ],
    });

    // Return the content from the first choice
    return completion.choices[0].message.content;
  } catch (error) {
    console.error('OpenAI API error:', error);
    throw new Error('Failed to generate response from OpenAI API');
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'api-gateway' });
});

// Main query endpoint
app.post('/query', async (req, res) => {
  try {
    const { query } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    // In a real implementation, this would retrieve context from vector database
    const context = 'Sample context from vector database';
    
    const response = await generateResponse(query, context);
    
    res.json({ 
      query,
      response,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error processing query:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});

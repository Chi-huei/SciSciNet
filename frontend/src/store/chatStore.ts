import { create } from 'zustand';
import { sendMessage as apiSendMessage } from '../api/client';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ChatStore {
  messages: Message[];
  currentVegaSpec: any;
  isLoading: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
  clearError: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  currentVegaSpec: null,
  isLoading: false,
  error: null,

  sendMessage: async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await apiSendMessage(text);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.text,
        sender: 'ai',
        timestamp: new Date(),
      };

      set((state) => ({
        messages: [...state.messages, aiMessage],
        currentVegaSpec: response.vega_spec,
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'An error occurred',
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));

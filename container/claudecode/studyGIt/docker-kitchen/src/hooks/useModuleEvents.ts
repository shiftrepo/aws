import { useCallback, useState } from 'react';
import { EventType } from '../interfaces/ModuleInterface';

/**
 * モジュール間イベント処理のためのカスタムフック
 * ダッシュボードとの統合時にイベント通信を簡素化する
 */
export const useModuleEvents = () => {
  // イベントハンドラのレジストリ
  const [eventHandlers] = useState<Record<string, Array<(data: any) => void>>>({});
  
  /**
   * イベントリスナーを登録する
   * @param eventType イベントタイプ
   * @param handler ハンドラー関数
   * @returns クリーンアップ用の解除関数
   */
  const addEventListener = useCallback((
    eventType: EventType | string,
    handler: (data: any) => void
  ) => {
    if (!eventHandlers[eventType]) {
      eventHandlers[eventType] = [];
    }
    
    eventHandlers[eventType].push(handler);
    
    // クリーンアップ用の解除関数を返す
    return () => {
      if (eventHandlers[eventType]) {
        const index = eventHandlers[eventType].indexOf(handler);
        if (index !== -1) {
          eventHandlers[eventType].splice(index, 1);
        }
      }
    };
  }, [eventHandlers]);
  
  /**
   * イベントを発火する
   * @param eventType イベントタイプ
   * @param data イベントデータ
   */
  const dispatchEvent = useCallback((
    eventType: EventType | string,
    data: any
  ) => {
    if (eventHandlers[eventType]) {
      eventHandlers[eventType].forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${eventType}:`, error);
        }
      });
    }
  }, [eventHandlers]);
  
  /**
   * ダッシュボードから提供される共通onEventハンドラ
   * @param event イベントタイプ
   * @param data イベントデータ
   */
  const onEvent = useCallback((event: string, data: any) => {
    dispatchEvent(event, data);
  }, [dispatchEvent]);
  
  return {
    addEventListener,
    dispatchEvent,
    onEvent
  };
};
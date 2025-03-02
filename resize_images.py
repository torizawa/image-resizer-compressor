import os
import sys
from PIL import Image
import glob

def resize_images(input_folder, output_folder, max_width=1300, max_size_kb=300):
    # 出力フォルダが存在しない場合は作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 対応する画像形式の拡張子
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']
    
    # 対象となるすべての画像ファイルを取得
    all_files = []
    for ext in image_extensions:
        all_files.extend(glob.glob(os.path.join(input_folder, ext)))
        all_files.extend(glob.glob(os.path.join(input_folder, ext.upper())))
    
    if not all_files:
        print(f"エラー: {input_folder} 内に画像ファイルが見つかりませんでした。")
        return
    
    # 最大サイズをバイト単位に変換
    max_size_bytes = max_size_kb * 1024
    
    print(f"処理対象の画像ファイル数: {len(all_files)}")
    
    for file_path in all_files:
        try:
            # ファイル名を取得
            filename = os.path.basename(file_path)
            output_path = os.path.join(output_folder, filename)
            
            # 画像を開く
            with Image.open(file_path) as img:
                # 画像のサイズを取得
                original_width, original_height = img.size
                
                # 幅が最大幅を超えている場合はリサイズ
                if original_width > max_width:
                    # アスペクト比を維持しながらリサイズ
                    ratio = max_width / original_width
                    new_height = int(original_height * ratio)
                    img = img.resize((max_width, new_height), Image.LANCZOS)
                    print(f"{filename} をリサイズしました: {original_width}x{original_height} -> {max_width}x{new_height}")
                
                # 画像の初期品質
                quality = 90  # より低い初期品質から開始
                
                # 目標サイズを超えないようにする
                while True:
                    # 一時的にメモリに保存
                    img.save(output_path, quality=quality, optimize=True)
                    current_size = os.path.getsize(output_path)
                    
                    # サイズが上限以下なら完了
                    if current_size <= max_size_bytes:
                        break
                    
                    # サイズが大きすぎる場合は品質を下げる
                    # より積極的に品質を下げる
                    quality_decrease = max(2, int((current_size - max_size_bytes) / (max_size_bytes * 0.05)))
                    quality -= quality_decrease
                    
                    # 最低品質を設定
                    quality = max(1, quality)
                    
                    # これ以上調整できない場合
                    if quality <= 1:
                        # 最後の手段としてサイズをさらに縮小
                        current_width, current_height = img.size
                        img = img.resize((int(current_width * 0.9), int(current_height * 0.9)), Image.LANCZOS)
                        quality = 80  # 品質をリセット
                        print(f"{filename} をさらにリサイズしました: {current_width}x{current_height} -> {int(current_width * 0.9)}x{int(current_height * 0.9)}")
            
            print(f"{filename} を処理しました。サイズ: {current_size/1024:.2f}KB、品質: {quality}")
            
        except Exception as e:
            print(f"エラー: {filename} の処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python resize_images.py 入力フォルダ 出力フォルダ")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    if not os.path.exists(input_folder):
        print(f"エラー: 入力フォルダ {input_folder} が存在しません。")
        sys.exit(1)
    
    resize_images(input_folder, output_folder)
    print("処理が完了しました。")

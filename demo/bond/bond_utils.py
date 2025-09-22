import akshare as ak
import pandas as pd
from pathlib import Path
import os
import time

class BondUtils:
    """可转债工具类，用于获取和处理可转债列表数据"""
    
    @staticmethod
    def get_all_bonds(save_path=None):
        """
        获取所有可转债列表
        
        参数:
        save_path: str, 可选，保存文件路径
        
        返回:
        DataFrame: 包含可转债代码和名称的DataFrame
        """
        try:
            # 获取全部可转债列表数据
            bond_df = ak.bond_zh_cov()
            
            # 仅保留需要的列：代码、名称、上市时间、发行规模和信用评级
            bond_df = bond_df[['债券代码', '债券简称', '上市时间', '发行规模', '信用评级']]
            
            # 重命名列
            bond_df = bond_df.rename(columns={
                '债券代码': 'bond_id',
                '债券简称': 'bond_name',
                '上市时间': 'listing_date',
                '发行规模': 'issue_size',
                '信用评级': 'credit_rating'
            })
            
            # 去除未上市的可转债（上市时间为NaN或为空字符串的记录）
            print(f"过滤前的可转债数量: {len(bond_df)}")
            bond_df = bond_df[bond_df['listing_date'].notna() & (bond_df['listing_date'] != '')]
            print(f"过滤后的可转债数量: {len(bond_df)}")
            
            # 保存到文件
            if save_path:
                # 确保目录存在
                save_dir = os.path.dirname(save_path)
                if save_dir and not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                bond_df.to_csv(save_path, index=False, encoding='utf-8-sig')
                print(f"可转债列表已保存至: {save_path}")
            
            return bond_df
        
        except Exception as e:
            print(f"获取可转债列表时出错: {str(e)}")
            return None
    
    @staticmethod
    def read_bonds_from_file(file_path):
        """
        从文件中读取可转债列表
        
        参数:
        file_path: str, 文件路径
        
        返回:
        DataFrame: 包含可转债代码和名称的DataFrame
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            bond_df = pd.read_csv(file_path, encoding='utf-8-sig')
            return bond_df
        
        except Exception as e:
            print(f"读取可转债列表文件时出错: {str(e)}")
            return None
    
    @staticmethod
    def ensure_bond_list_exists(file_path):
        """
        确保可转债列表文件存在，如果不存在则创建
        
        参数:
        file_path: str, 文件路径
        
        返回:
        DataFrame: 包含可转债代码和名称的DataFrame
        """
        if os.path.exists(file_path):
            return BondUtils.read_bonds_from_file(file_path)
        else:
            return BondUtils.get_all_bonds(file_path) 
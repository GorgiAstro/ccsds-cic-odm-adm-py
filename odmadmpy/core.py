from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Generator


class Oadm:
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    odm_type = ''
    revision = ''

    def __init__(self, originator: str, standard: Optional[str] = 'CCSDS'):
        self.originator = originator
        self.standard = standard

    def format_time_string(self, date: datetime) -> str:
        return date.strftime(self.time_format)[:-3]

    def format_time_vector(self, df: pd.DataFrame) -> np.array:
        if self.standard == 'CCSDS':
            if 'datetime' not in df:
                print('Not good')  # TODO: raise exception
            return df['datetime'].apply(lambda x: self.format_time_string(x))
        elif self.standard == 'CIC':
            if 'MJD' not in df:
                print('Not good')  # TODO: raise exception
            return df['MJD'].apply(lambda x: f'{int(x)} {int(86400 * (x - int(x)))}')

    def format_header(self, comments: Optional[List[str]] = []) -> Generator[str, None, None]:
        yield f'{self.standard}_{self.odm_type}_VERS = {self.revision}'
        for comment in comments:
            yield f'COMMENT {comment}'
        yield f'CREATION_DATE = {self.format_time_string(datetime.utcnow())}'
        yield f'ORIGINATOR = {self.originator}'
        yield ''

    def write_file(self, segments: List[str], filename: str, comments: Optional[List[str]] = []) -> None:
        with open(filename, 'w') as file:
            file.writelines('\n'.join(self.format_header(comments)))
            file.writelines('\n'.join(segments))
            file.writelines('\n')


class Aem(Oadm):
    odm_type = 'AEM'
    revision = '1.0'

    meta_mandat_keys = {
        'OBJECT_NAME',
        'OBJECT_ID',
        'REF_FRAME_A',
        'REF_FRAME_B',
        'ATTITUDE_DIR',
        'TIME_SYSTEM',
        'ATTITUDE_TYPE',
    }
    meta_opt_allowed = {
        'CENTER_NAME',
        'USEABLE_START_TIME',
        'USEABLE_STOP_TIME',
        'QUATERNION_TYPE',
        'EULER_ROT_SEQ',
        'RATE_FRAME',
        'INTERPOLATION_METHOD',
        'INTERPOLATION_DEGREE'
    }

    @staticmethod
    def sample_meta_mandat() -> Dict[str, str]:
        meta_mandat = {
            'OBJECT_NAME': 'MARS GLOBAL SURVEYOR',
            'OBJECT_ID': '1996-062A',
            'REF_FRAME_A': 'EME2000',
            'REF_FRAME_B': 'SC_BODY_1',
            'ATTITUDE_DIR': 'A2B',
            'TIME_SYSTEM': 'UTC',
            'ATTITUDE_TYPE': 'QUATERNION',
        }
        return meta_mandat

    @staticmethod
    def sample_meta_opt() -> Dict[str, str]:
        meta_opt = {
            'CENTER_NAME': 'mars barycenter',
            'USEABLE_START_TIME': datetime(1996, 11, 28, 22, 8, 2, 555500),
            'USEABLE_STOP_TIME': datetime(1996, 11, 30, 1, 18, 2, 555500),
            'QUATERNION_TYPE': 'LAST',
            'INTERPOLATION_METHOD': 'hermite',
            'INTERPOLATION_DEGREE': 7
        }
        return meta_opt

    def format_segment(self, df: pd.DataFrame, meta_mandat: Dict[str, str], meta_opt: Optional[Dict[str, str]] = {},
                       comments_meta: Optional[List[str]] = [], comments_data: Optional[List[str]] = []) \
            -> Generator[str, None, None]:
        yield ''
        yield 'META_START'

        for comment in comments_meta:
            yield f'COMMENT {comment}'

        yield f'OBJECT_NAME = {meta_mandat["OBJECT_NAME"]}'
        yield f'OBJECT_ID = {meta_mandat["OBJECT_ID"]}'
        if 'CENTER_NAME' in meta_opt:
            yield f'CENTER_NAME = {meta_opt["CENTER_NAME"]}'
        yield f'REF_FRAME_A = {meta_mandat["REF_FRAME_A"]}'
        yield f'REF_FRAME_B = {meta_mandat["REF_FRAME_B"]}'
        yield f'ATTITUDE_DIR = {meta_mandat["ATTITUDE_DIR"]}'

        yield f'TIME_SYSTEM = {meta_mandat["TIME_SYSTEM"]}'
        if self.standard == 'CCSDS':
            yield f'START_TIME = {self.format_time_string(df.iloc[0]["datetime"])}'
            if 'USEABLE_START_TIME' in meta_opt:
                yield f'USEABLE_START_TIME = {self.format_time_string(meta_opt["USEABLE_START_TIME"])}'
            if 'USEABLE_STOP_TIME' in meta_opt:
                yield f'USEABLE_STOP_TIME = {self.format_time_string(meta_opt["USEABLE_STOP_TIME"])}'
            yield f'STOP_TIME = {self.format_time_string(df.iloc[-1]["datetime"])}'

        yield f'ATTITUDE_TYPE = {meta_mandat["ATTITUDE_TYPE"]}'
        if 'QUATERNION_TYPE' in meta_opt:
            yield f'QUATERNION_TYPE = {meta_opt["QUATERNION_TYPE"]}'

        if 'INTERPOLATION' in meta_opt:
            yield f'INTERPOLATION = {meta_opt["INTERPOLATION"]}'
        if 'INTERPOLATION_DEGREE' in meta_opt:
            yield f'INTERPOLATION_DEGREE = {meta_opt["INTERPOLATION_DEGREE"]}'

        yield 'META_STOP'

        for comment in comments_data:
            yield f'COMMENT {comment}'

        yield ''

        df['format_time_string'] = self.format_time_vector(df)

        for index, row in df.iterrows():
            row_str = ''
            row_str += f'{row["format_time_string"]}'
            if 'QUATERNION_TYPE' in meta_opt and meta_opt["QUATERNION_TYPE"] == 'LAST':
                row_str += f'  {row["qx"]:.9f} {row["qy"]:.9f} {row["qz"]:.9f} {row["qs"]:.9f}'
            else:
                row_str += f'  {row["qs"]:.9f} {row["qx"]:.9f} {row["qy"]:.9f} {row["qz"]:.9f}'
            yield row_str


class Oem(Oadm):
    odm_type = 'OEM'
    revision = '2.0'

    meta_mandat_keys = {
        'OBJECT_NAME',
        'OBJECT_ID',
        'CENTER_NAME',
        'REF_FRAME',
        'TIME_SYSTEM'
    }
    meta_opt_allowed = {
        'REF_FRAME_EPOCH',
        'USEABLE_START_TIME',
        'USEABLE_STOP_TIME',
        'INTERPOLATION',
        'INTERPOLATION_DEGREE',
    }

    @staticmethod
    def sample_meta_mandat() -> Dict[str, str]:
        meta_mandat = {
            'OBJECT_NAME': 'STS 106',
            'OBJECT_ID': '2000-053A',
            'CENTER_NAME': 'EARTH',
            'REF_FRAME': 'EME2000',
            'TIME_SYSTEM': 'TAI'
        }
        return meta_mandat

    @staticmethod
    def sample_meta_opt() -> Dict[str, str]:
        meta_opt = {
            'REF_FRAME_EPOCH': datetime(2000, 1, 1),
            'USEABLE_START_TIME': datetime(1996, 12, 18, 12, 10, 0, 331000),
            'USEABLE_STOP_TIME': datetime(1996, 12, 18, 21, 23, 0, 331000),
            'INTERPOLATION': 'HERMITE',
            'INTERPOLATION_DEGREE': 7,
        }
        return meta_opt

    def format_segment(self, df: pd.DataFrame, meta_mandat: Dict[str, str], meta_opt: Optional[Dict[str, str]] = {},
                       comments_meta: Optional[List[str]] = [], comments_data: Optional[List[str]] = [])\
            -> Generator[str, None, None]:
        yield ''
        yield 'META_START'

        for comment in comments_meta:
            yield f'COMMENT {comment}'

        yield f'OBJECT_NAME = {meta_mandat["OBJECT_NAME"]}'
        yield f'OBJECT_ID = {meta_mandat["OBJECT_ID"]}'
        yield f'CENTER_NAME = {meta_mandat["CENTER_NAME"]}'
        yield f'REF_FRAME = {meta_mandat["REF_FRAME"]}'

        if 'REF_FRAME_EPOCH' in meta_opt:
            yield f'REF_FRAME_EPOCH = {self.format_time_string(meta_opt["REF_FRAME_EPOCH"])}'

        yield f'TIME_SYSTEM = {meta_mandat["TIME_SYSTEM"]}'
        if self.standard == 'CCSDS':
            yield f'START_TIME = {self.format_time_string(df.iloc[0]["datetime"])}'
            if 'USEABLE_START_TIME' in meta_opt:
                yield f'USEABLE_START_TIME = {self.format_time_string(meta_opt["USEABLE_START_TIME"])}'
            if 'USEABLE_STOP_TIME' in meta_opt:
                yield f'USEABLE_STOP_TIME = {self.format_time_string(meta_opt["USEABLE_STOP_TIME"])}'
            yield f'STOP_TIME = {self.format_time_string(df.iloc[-1]["datetime"])}'

        if 'INTERPOLATION' in meta_opt:
            yield f'INTERPOLATION = {meta_opt["INTERPOLATION"]}'
        if 'INTERPOLATION_DEGREE' in meta_opt:
            yield f'INTERPOLATION_DEGREE = {meta_opt["INTERPOLATION_DEGREE"]}'

        yield 'META_STOP'

        for comment in comments_data:
            yield f'COMMENT {comment}'

        yield ''

        df['format_time_string'] = self.format_time_vector(df)

        has_acceleration = 'ax' in df

        for index, row in df.iterrows():
            row_str = ''
            row_str += f'{row["format_time_string"]}'
            row_str += f'  {1e-3 * row["x"]:.6f} {1e-3 * row["y"]:.6f} {1e-3 * row["z"]:.6f}'
            row_str += f'  {1e-3 * row["vx"]:.9f} {1e-3 * row["vy"]:.9f} {1e-3 * row["vz"]:.9f}'
            if has_acceleration:
                row_str += f'  {1e-3 * row["ax"]:.6f} {1e-3 * row["ay"]:.6f} {1e-3 * row["az"]:.6f}'
            yield row_str

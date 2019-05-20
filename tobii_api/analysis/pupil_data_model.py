import logging

import numpy as np

LOG = logging.getLogger(__name__)
NaN = float('nan')


def madCalc(d, n):
    med_n   = np.nanmedian(d)
    mad     = np.nanmedian( np.abs(d - med_n)  )
    thresh  = med_n + (n * mad)
    return med_n, mad, thresh    


class PupilDataModel:
    

    CSV_FILE_NAME   = 'pd_table.csv'
    CSV_L_FILE_NAME = 'pd_timeseries_left.csv'
    CSV_R_FILE_NAME = 'pd_timeseries_right.csv'

    # Default values according to Kret et al. 2018 and corresponding source code
    # see https://github.com/ElioS-S/pupil-size/blob/master/code/helperFunctions/rawDataFilter.m
    
    # Pupil range filter criteria
    PD_MIN              = 1.5
    PD_MAX              = 9.0

    # Isolated sample filter criteria
    MAX_SEP             = 40000         # 40ms     (timestamps are in nanoseconds)
    MIN_ISLAND_WIDTH    = 50000         # 50ms     (timestamps are in nanoseconds)

    # Dilation speed filter criteria
    MAD_MULTIPLIER      = 16
    MAX_GAP_MS          = 200000        # 200ms    (timestamps are in nanoseconds)


    GAP_MIN             = 75000         # 75ms     (timestamps are in nanoseconds)
    GAP_MAX             = 2000000       # 2000ms   (timestamps are in nanoseconds)
    GAP_PAD             = 50000         # 50ms     (timestamps are in nanoseconds)

    BLINK_MIN           = 100000
    BLINK_MAX           = 250000

    
    def __init__(self, table):
        
        # preserve all timestamps in case some get lost during filtering
        self._ts            = np.array([row[0] for row in table], np.uint64)

        self.ts_l           = []
        self.pd_l           = []
        
        self.ts_r           = []
        self.pd_r           = []

        self._ts_l_filtered = None
        self._ts_r_filtered = None

        self._pd_l_filtered = None
        self._pd_r_filtered = None
        
        # only import valid data
        for ts, _, s_l, pd_l, s_r, pd_r in table:
            if s_l == 0 and pd_l > 0:
                self.ts_l.append(ts)
                self.pd_l.append(pd_l)

            if s_r == 0 and pd_r > 0:
                self.ts_r.append(ts)
                self.pd_r.append(pd_r)

        self.ts_l = np.array(self.ts_l, np.uint64)      # uint64 is necessary for timestamps!
        self.ts_r = np.array(self.ts_r, np.uint64)      # uint64 is necessary for timestamps!

        self.pd_l = np.array(self.pd_l, np.float64)
        self.pd_r = np.array(self.pd_r, np.float64)
        
        # double check that all timestamps strictly increasing
        assert np.all(np.diff(self.ts_l) > 0)
        
        self._removedLog('Import', table, self.ts_l)
        self._removedLog('Import', table, self.ts_r)

        
    def _removedLog(self, filter_name, full, filtered):
        """ Just a convenience method for logging of removed samples. """
        len_full    = len(full)
        count       = len_full - len(filtered)
        ratio       = count * 1.0 / len_full
        LOG.debug('%s Filter:\t%5.d\t[%.4f%%] samples removed.' % (filter_name, count, ratio))


    @property
    def ts(self):
        """ Returns all timestamps no matter if there was valid data at the timestamps. """
        return self._ts

    @property
    def eye_left(self):
        return self.ts_l, self.pd_l


    @property
    def eye_right(self):
        return self.ts_r, self.pd_r
    
    
    @property
    def eye_left_filtered(self):
        
        # return if already calculated
        if self._ts_l_filtered is not None:
            return self._ts_l_filtered, self._pd_l_filtered
        
        self._ts_l_filtered, self._pd_l_filtered = self._filter(self.ts_l, self.pd_l)
        return self._ts_l_filtered, self._pd_l_filtered


    @property
    def eye_right_filtered(self):

        # return if already calculated
        if self._ts_r_filtered is not None:
            return self._ts_r_filtered, self._pd_r_filtered
        
        self._ts_r_filtered, self._pd_r_filtered = self._filter(self.ts_r, self.pd_r)
        return self._ts_r_filtered, self._pd_r_filtered


    def _filter(self, ts, pd):
        ts, pd = self.filterRange(ts, pd)
        ts, pd = self.filterLoners(ts, pd)
        ts, pd = self.filterSpeed(ts, pd)
        ts, pd = self.filterLoners(ts, pd)
        ts, pd = self.expandGaps(ts, pd)
        return ts, pd


    def _remove_indices(self, reason, ts, pd, index_list):
        """ Remove the elements corresponding to the indices in the index_list and log it. """
        new_ts      = np.delete(ts, index_list)
        new_pd      = np.delete(pd, index_list)
        self._removedLog(reason, ts, new_ts)
        return new_ts, new_pd
        

    def filterRange(self, ts, pd, pd_min = PD_MIN, pd_max = PD_MAX):
        """ Filters a pupil diameter time series by thresholding using pd_min and pd_max values. """ 
        return self._remove_indices('Range', ts, pd, np.argwhere((pd < pd_min) | (pd > pd_max)))


    def filterLoners(self, ts, pd, max_sep = MAX_SEP, min_island_width = MIN_ISLAND_WIDTH):
        assert len(ts) == len(pd)
        assert len(ts) > 3

        edges = np.argwhere(np.diff(ts) > max_sep).flatten()

        # find size, start and length of all islands
        islands = []
        for idx in range(len(edges) - 1):
            edge_l = edges[idx] + 1
            edge_r = edges[idx+1]
            size   = ts[edge_r] - ts[edge_l]
            islands.append( (size, edge_l, edge_r - edge_l + 1) )
        
        # filter islands that are too small
        tiny_islands = [(idx, length) for size, idx, length in islands if size < min_island_width]

        # expand indices
        index_list = []
        for idx, length in tiny_islands:
            index_list.extend([idx + i for i in range(length)])

        return self._remove_indices('Loner', ts, pd, index_list)


    def filterSpeed(self, ts, pd, max_gap_ms = MAX_GAP_MS, mad_multiplier = MAD_MULTIPLIER):
        assert len(ts) == len(pd)
        assert len(ts) > 3

        dts                = np.diff(ts)
        dpd                = np.abs(np.diff(pd))

        # Calculate the dilation speeds:
        curDilationSpeeds  = dpd / dts

        # The maximum gap over which a change is considered:
        curDilationSpeeds  = np.where(dts < max_gap_ms, curDilationSpeeds, NaN)

        # Generate a two column array with the back and forward dilation speeds:
        backFwdDilations   = np.array( [ np.append( [NaN],             curDilationSpeeds), 
                                         np.append( curDilationSpeeds, [NaN])              ] )

        # Calculate the deviation per sample:
        maxDilationSpeeds  = np.nanmax(backFwdDilations, axis = 0)

        # Calculate the MAD stats:
        med_d, mad, thresh = madCalc(maxDilationSpeeds, mad_multiplier)

        LOG.debug("MEDIAN:\t%.10f\tMAD:\t%.10f\tThreshold:\t%.10f" % (med_d, mad, thresh))

        # Determine the outliers and remove them:
        return self._remove_indices('Speed', ts, pd, np.argwhere(maxDilationSpeeds > thresh))
    
    
    def expandGaps(self, ts, pd, gap_min = GAP_MIN, gap_max = GAP_MAX, gap_pad = GAP_PAD):
        assert len(ts) == len(pd)
        assert len(ts) > 3

        dts         = np.diff(ts)
        tsl         = len(ts)
        index_list  = []

        # for all gap locations that match the constraints
        for gap_idx in np.argwhere((dts > gap_min) & (dts < gap_max)).flatten():
            
            edge_r  = gap_idx
            edge_l  = gap_idx + 1 
            erode_r = ts[edge_r] - gap_pad
            erode_l = ts[edge_l] + gap_pad

            # erode right
            for i in range(edge_r, 0, -1):
                if ts[i] > erode_r:
                    index_list.append(i)
                else:
                    break
                
            # erode left
            for i in range(edge_l, tsl):
                if ts[i] < erode_l:
                    index_list.append(i)
                else:
                    break
                
        return self._remove_indices('Erosion', ts, pd, index_list)
    
    
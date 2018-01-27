import os
import numpy as np
from osgeo import gdal
import csv

bratCaps = ['05', '25', '50', '100']
#bratCaps = ['05']
for bratCap in bratCaps:
    modelDir = "03_out_" + bratCap
    modDir = "MODFLOW_" + bratCap
    huc8 = str(16010204)
    path = 'E:/konrad/Projects/Modeling/BeaverWaterStorage/wrk_Data/AnalysisRuns/BearRiverHUC8/'+ huc8 + '/HUC12'
    outfile = 'E:/konrad\Projects/Modeling/BeaverWaterStorage/wrk_Data/AnalysisRuns/BearRiverHUC8/'+ huc8 + '/OverallResults' + '/' + modDir + '_yield.csv'
    inDir = "02_rasIn"
    os.chdir(path)
    ofile = open(outfile, 'wb')
    writer = csv.writer(ofile)
    row = ["huc12", "brat_cap","surface_lo", "surface_mid", "surface_hi", "gw_lo", "gw_mid", "gw_hi"]
    writer.writerow(row)

    subdirs = [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]
    for subdir in subdirs:
        if os.path.exists(subdir + "/" + modelDir + "/depMid.tif"):
            #print subdir + " running " + os.path.relpath(subdir, path)
            os.chdir(subdir)

            gwlo = 0.0
            gwmid = 0.0
            gwhi = 0.0

            porDs = gdal.Open(inDir + "/por_vbfac.tif")
            fcDs = gdal.Open(inDir + "/fc_vbfac.tif")
            geot = porDs.GetGeoTransform()

            pndloDS = gdal.Open(modelDir + '/depLo.tif')
            pndmidDS = gdal.Open(modelDir + '/depMid.tif')
            pndhiDS = gdal.Open(modelDir + '/depHi.tif')
            porData = porDs.GetRasterBand(1).ReadAsArray()
            fcData = fcDs.GetRasterBand(1).ReadAsArray()
            pnd = porDs.GetRasterBand(1).GetNoDataValue()
            fcnd = fcDs.GetRasterBand(1).GetNoDataValue()
            porData[porData == pnd] = np.nan
            fcData[fcData == fcnd] = np.nan
            porData = porData/100.0
            fcData = fcData / 100.0

            sloData = pndloDS.GetRasterBand(1).ReadAsArray()
            sloData[sloData < 0.0] = 0.0
            smidData = pndmidDS.GetRasterBand(1).ReadAsArray()
            smidData[smidData < 0.0] = 0.0
            shiData = pndhiDS.GetRasterBand(1).ReadAsArray()
            shiData[shiData < 0.0] = 0.0
            slo = np.nansum(sloData) * abs(geot[1]) * abs(geot[5])
            smid = np.nansum(smidData) * abs(geot[1]) * abs(geot[5])
            shi = np.nansum(shiData) * abs(geot[1]) * abs(geot[5])

            porData = porData-fcData

            if os.path.exists(modDir + "/hdch_lo.tif"):
                #volume for low dam height water table change
                hdloDS = gdal.Open(modDir + '/hdch_lo.tif')
                hdlo = hdloDS.GetRasterBand(1).ReadAsArray()
                lond = hdloDS.GetRasterBand(1).GetNoDataValue()
                hdlo[hdlo == lond] = np.nan
                hdlo[hdlo < -1.0] = np.nan
                volLoPor = np.multiply(porData, hdlo)
                gwlo = np.nansum(volLoPor) * abs(geot[1]) * abs(geot[5])

                write2 = np.where(np.isnan(volLoPor), -9999.0, volLoPor)
                hdch_dslo = gdal.GetDriverByName('GTiff').Create(modDir + '/hdch_lo_yield.tif', porDs.RasterXSize,
                                                                 porDs.RasterYSize, 1, gdal.GDT_Float32)
                hdch_dslo.SetProjection(porDs.GetProjection())
                hdch_dslo.SetGeoTransform(geot)
                hdch_dslo.GetRasterBand(1).WriteArray(write2)
                hdch_dslo.GetRasterBand(1).FlushCache()
                hdch_dslo.GetRasterBand(1).SetNoDataValue(-9999.0)

            if os.path.exists(modDir + "/hdch_mid.tif"):
                # volume for mid dam height water table change
                hdmidDS = gdal.Open(modDir + '/hdch_mid.tif')
                hdmid = hdmidDS.GetRasterBand(1).ReadAsArray()
                midnd = hdmidDS.GetRasterBand(1).GetNoDataValue()
                hdmid[hdmid == midnd] = np.nan
                hdmid[hdmid < -1.0] = np.nan
                volMidPor = np.multiply(porData, hdmid)
                gwmid = np.nansum(volMidPor) * abs(geot[1]) * abs(geot[5])

                write2 = np.where(np.isnan(volMidPor), -9999.0, volMidPor)
                hdch_dsmid = gdal.GetDriverByName('GTiff').Create(modDir + '/hdch_mid_yield.tif', porDs.RasterXSize,
                                                                 porDs.RasterYSize, 1, gdal.GDT_Float32)
                hdch_dsmid.SetProjection(porDs.GetProjection())
                hdch_dsmid.SetGeoTransform(geot)
                hdch_dsmid.GetRasterBand(1).WriteArray(write2)
                hdch_dsmid.GetRasterBand(1).FlushCache()
                hdch_dsmid.GetRasterBand(1).SetNoDataValue(-9999.0)

            if os.path.exists(modDir + "/hdch_hi.tif"):
                # volume for high dam height water table change
                hdhiDS = gdal.Open(modDir + '/hdch_hi.tif')
                hdhi = hdhiDS.GetRasterBand(1).ReadAsArray()
                hind = hdhiDS.GetRasterBand(1).GetNoDataValue()
                hdhi[hdhi == hind] = np.nan
                hdhi[hdhi < -1.0] = np.nan
                volHiPor = np.multiply(porData, hdhi)
                gwhi = np.nansum(volHiPor) * abs(geot[1]) * abs(geot[5])

                write2 = np.where(np.isnan(volHiPor), -9999.0, volHiPor)
                hdch_dshi = gdal.GetDriverByName('GTiff').Create(modDir + '/hdch_hi_yield.tif', porDs.RasterXSize,
                                                                 porDs.RasterYSize, 1, gdal.GDT_Float32)
                hdch_dshi.SetProjection(porDs.GetProjection())
                hdch_dshi.SetGeoTransform(geot)
                hdch_dshi.GetRasterBand(1).WriteArray(write2)
                hdch_dshi.GetRasterBand(1).FlushCache()
                hdch_dshi.GetRasterBand(1).SetNoDataValue(-9999.0)

            row = [subdir, bratCap, slo, smid, shi, gwlo, gwmid, gwhi]
            print row
            writer.writerow(row)
            os.chdir(path)

        else:
            gwlo = 0.0
            gwmid = 0.0
            gwhi = 0.0
            slo = 0.0
            smid = 0.0
            shi = 0.0
            print("NOT CALCULATED FOR: " + os.path.relpath(subdir, path))
            row = [subdir, bratCap, slo, smid, shi, gwlo, gwmid, gwhi]
            print row
            writer.writerow(row)

    ofile.close()
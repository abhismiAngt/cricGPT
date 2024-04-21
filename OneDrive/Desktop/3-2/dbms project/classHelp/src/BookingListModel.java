
//import java.awt.List;
import java.util.*;
import javax.swing.AbstractListModel;
import javax.swing.JPanel;
import javax.swing.AbstractListModel;
import javax.swing.JPanel;
import java.util.ArrayList;
import java.util.List;


/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */

/**
 *
 * @author 91995
 */
class BookingListModel extends AbstractListModel<JPanel> {
    private List<JPanel> bookings = new ArrayList<>();

    public void setBookings(List<JPanel> bookings) {
        this.bookings = bookings;
        fireContentsChanged(this, 0, getSize());
    }

    @Override
    public int getSize() {
        return bookings.size();
    }

    @Override
    public JPanel getElementAt(int index) {
        return bookings.get(index);
    }
}

